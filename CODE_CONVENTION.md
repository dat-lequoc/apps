- write short, concise, compact code
- data should be simple a json object, each app can have a table, but all the data should be stored in a single json object
- Remember avoid bugs when update the data, """            .upsert(payload, { 
              onConflict: 'user_id',
              ignoreDuplicates: false 
            });"""
