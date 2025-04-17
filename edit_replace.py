import re
import sys
import os  # For file operations like remove
import shutil # For safely moving the file

def extract_replace_blocks(text):
    """
    Extracts code blocks marked with '>>>>>>> REPLACE' from text containing
    git merge conflict markers.

    Args:
        text: The input string containing merge conflict markers.

    Returns:
        A list of strings, where each string is the content of a 'REPLACE' block.
    """
    # Regex to find the content between ======= and >>>>>>> REPLACE
    # It handles potential variations in spacing and line endings.
    # (?s) makes . match newline characters
    pattern = re.compile(r"=======\n(.*?)\n>>>>>>> REPLACE", re.DOTALL)

    matches = pattern.findall(text)

    # Clean up trailing whitespace that might be captured, keeping leading whitespace
    return [match.rstrip() for match in matches]

def extract_search_blocks(text):
    """
    Extracts code blocks marked with '<<<<<<< SEARCH' from text containing
    git merge conflict markers.

    Args:
        text: The input string containing merge conflict markers.

    Returns:
        A list of strings, where each string is the content of a 'SEARCH' block.
    """
    # Regex to find the content between <<<<<<< SEARCH and =======
    # It handles potential variations in spacing and line endings.
    pattern = re.compile(r"<<<<<<< SEARCH\n(.*?)\n=======", re.DOTALL)

    matches = pattern.findall(text)

    # Clean up trailing whitespace, keep leading whitespace
    return [match.rstrip() for match in matches]

# --- Argument Parsing and File Reading ---

# Check if correct number of filenames were provided
if len(sys.argv) != 3:
    print(f"Usage: python {sys.argv[0]} <marker_filename> <target_filename>")
    print("  <marker_filename>: File containing <<<<<<< SEARCH / >>>>>>> REPLACE blocks.")
    print("  <target_filename>: File to apply the replacements to.")
    sys.exit(1)

marker_filename = sys.argv[1]
target_filename = sys.argv[2]
marker_text = ""
target_content = ""

# Read the marker file
try:
    with open(marker_filename, 'r', encoding='utf-8') as f:
        marker_text = f.read()
except FileNotFoundError:
    print(f"Error: Marker file not found: {marker_filename}")
    sys.exit(1)
except Exception as e:
    print(f"Error reading marker file '{marker_filename}': {e}")
    sys.exit(1)

# Read the target file
try:
    with open(target_filename, 'r', encoding='utf-8') as f:
        target_content = f.read()
except FileNotFoundError:
    print(f"Error: Target file not found: {target_filename}")
    sys.exit(1)
except Exception as e:
    print(f"Error reading target file '{target_filename}': {e}")
    sys.exit(1)

# --- Block Extraction and Processing ---

extracted_replace_blocks = extract_replace_blocks(marker_text)
extracted_search_blocks = extract_search_blocks(marker_text)

num_replace_blocks = len(extracted_replace_blocks)
num_search_blocks = len(extracted_search_blocks)
modified_content = target_content
replacements_made_count = 0
blocks_not_found = []

if num_replace_blocks == 0 and num_search_blocks == 0:
    print(f"\nNo '<<<<<<< SEARCH' or '>>>>>>> REPLACE' blocks found in marker file '{marker_filename}'. No changes made to '{target_filename}'.")
    sys.exit(0)

num_pairs = 0
if num_replace_blocks != num_search_blocks:
    num_pairs = min(num_search_blocks, num_replace_blocks)
    print(f"\nWarning: Mismatched number of SEARCH ({num_search_blocks}) and REPLACE ({num_replace_blocks}) blocks in '{marker_filename}'.")
    print(f"--- Processing {num_pairs} Paired SEARCH/REPLACE Blocks against '{target_filename}' ---")
    # Optional: print warnings about leftover blocks if needed
else:
    num_pairs = num_search_blocks
    print(f"\n--- Processing {num_pairs} Paired SEARCH/REPLACE Blocks against '{target_filename}' ---")


if num_pairs > 0:
    for i in range(num_pairs):
        search_block = extracted_search_blocks[i]
        replace_block = extracted_replace_blocks[i]

        # --- DEBUGGING: Print the exact search block ---
        print("-" * 10 + f" DEBUG: Searching for Block {i+1} " + "-" * 10)
        print(f"Raw search block (using repr):\n{repr(search_block)}")
        print("-" * 10 + f" END DEBUG Block {i+1} " + "-" * 10)
        # --- END DEBUGGING ---

        # Count occurrences before replacing
        occurrences = modified_content.count(search_block)

        if occurrences > 0:
            modified_content = modified_content.replace(search_block, replace_block)
            print(f"  Applied Block Pair {i+1}: Replaced {occurrences} occurrence(s).")
            replacements_made_count += occurrences
        else:
            print(f"  Warning: SEARCH Block {i+1} not found in '{target_filename}'.")
            blocks_not_found.append(i + 1)

# --- Save, Confirm, and Overwrite ---

if replacements_made_count > 0:
    temp_filename = target_filename + ".modified"
    print(f"\nTotal replacements made: {replacements_made_count}")
    if blocks_not_found:
        print(f"Warning: SEARCH blocks not found for pair numbers: {blocks_not_found}")

    try:
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"\nModified content written to temporary file: '{temp_filename}'")
    except Exception as e:
        print(f"\nError writing temporary file '{temp_filename}': {e}")
        sys.exit(1)

    # Ask for confirmation
    while True:
        confirm = input(f"Review '{temp_filename}'. Overwrite original file '{target_filename}'? (yes/no): ").lower()
        if confirm == 'yes':
            try:
                shutil.move(temp_filename, target_filename)
                print(f"Successfully replaced '{target_filename}'.")
            except Exception as e:
                print(f"\nError replacing original file: {e}")
                print(f"Modified content remains in '{temp_filename}'.")
            break
        elif confirm == 'no':
            try:
                os.remove(temp_filename)
                print(f"Operation cancelled. Temporary file '{temp_filename}' removed.")
            except Exception as e:
                print(f"\nError removing temporary file '{temp_filename}': {e}")
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

elif num_pairs > 0: # Processed pairs but no replacements were made
     print(f"\nNo matching SEARCH blocks found in '{target_filename}'. Original file remains unchanged.")
# else: case already handled where no blocks were found in marker file initially
