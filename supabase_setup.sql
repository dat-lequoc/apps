-- Drop existing notes table if it exists
drop table if exists notes;

-- Create new notes table with JSON data column
create table notes (
  id bigint generated by default as identity primary key,
  user_id uuid references auth.users not null,
  data jsonb not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Set up RLS (Row Level Security)
alter table notes enable row level security;

-- Create policy to allow users to only see their own notes
create policy "Users can only access their own notes"
  on notes for all
  using (auth.uid() = user_id);