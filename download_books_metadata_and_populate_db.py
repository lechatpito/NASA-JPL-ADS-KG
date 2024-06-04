import requests
import gzip
import json
import psycopg2
import io
import os


URLS_FILE="ads_metadata_urls.txt"

# Get the database username and password from environment variables
db_user = os.getenv('PG_DB_USER')
db_password = os.getenv('PG_DB_PASSWORD')

# Connect to your postgres DB
conn = psycopg2.connect(f"dbname=ads user={db_user} password={db_password}")


# Open a cursor to perform database operations
cur = conn.cursor()

# Create table
cur.execute("""
CREATE TABLE books (
    bibcode TEXT PRIMARY KEY,
    author TEXT[],
    bibstem TEXT[],
    doctype TEXT,
    doi TEXT[],
    id TEXT,
    identifier TEXT[],
    pub TEXT,
    pubdate DATE,
    title TEXT[],
    institution TEXT,
    keyword_schema TEXT,
    keyword TEXT,
    keyword_norm TEXT,
    abstract TEXT
);
""")

# Commit the changes
conn.commit()

# Open the file with the list of URLs
with open(URLS_FILE, 'r') as file:
    urls = file.readlines()

# Go through each URL
for url in urls:
    url = url.strip()
    print(url)

    # Download the file
    r = requests.get(url)

    # Unzip the file
    zipped_file = gzip.decompress(r.content)

    # Convert the bytes to string
    json_str = zipped_file.decode('utf-8')
    
    # Split the string into lines
    lines = json_str.split('\n')

    # Convert each book entry to a SQL statement and load it to the database
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Parse the line as a JSON object
        book = json.loads(line)
        
        # Convert each book entry to a SQL statement and load it to the database
        for book in data:
            cur.execute("""
            INSERT INTO books (bibcode, author, bibstem, doctype, doi, id, identifier, pub, pubdate, title, institution, keyword_schema, keyword, keyword_norm, abstract)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (bibcode) DO UPDATE SET
            author = EXCLUDED.author,
            bibstem = EXCLUDED.bibstem,
            doctype = EXCLUDED.doctype,
            doi = EXCLUDED.doi,
            id = EXCLUDED.id,
            identifier = EXCLUDED.identifier,
            pub = EXCLUDED.pub,
            pubdate = EXCLUDED.pubdate,
            title = EXCLUDED.title,
            institution = EXCLUDED.institution,
            keyword_schema = EXCLUDED.keyword_schema,
            keyword = EXCLUDED.keyword,
            keyword_norm = EXCLUDED.keyword_norm,
            abstract = EXCLUDED.abstract;
            """, (book['bibcode'], book['author'], book['bibstem'], book['doctype'], book['doi'], book['id'], book['identifier'], book['pub'], book['pubdate'], book['title'], book['institution'], book['keyword_schema'], book['keyword'], book['keyword_norm'], book['abstract']))

    # Commit the changes
    conn.commit()

# Close communication with the database
cur.close()
conn.close()
