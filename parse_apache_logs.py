import re
import zipfile
import io
from datetime import datetime
import pandas as pd
from pathlib import Path

# --- Config: path to the zip file ---
zip_path = Path("apache_logs.txt.zip")   # adjust path if different
log_filename_inside_zip = "apache_logs.txt"  # change if different name

# --- Regex for Apache combined log format ---
pattern = re.compile(
    r'(?P<host>\S+) '              # host %h
    r'\S+ \S+ '                    # ident (%l) and authuser (%u) - ignored here
    r'\[(?P<timestamp>[^\]]+)\] '  # timestamp %t
    r'"(?P<method>\S+) '           # request method
    r'(?P<resource>\S+) '          # resource requested (URL path)
    r'(?P<protocol>[^"]+)" '       # protocol (HTTP/1.1)
    r'(?P<status>\d{3}) '          # status code
    r'(?P<size>\S+) '              # response size in bytes (or -)
    r'"(?P<referrer>[^"]*)" '      # referrer
    r'"(?P<user_agent>[^"]*)"'     # user agent
)

def parse_line(line):
    m = pattern.match(line)
    if not m:
        return None
    d = m.groupdict()
    # normalize fields
    d['size'] = None if d['size'] == '-' else int(d['size'])
    try:
        d['timestamp'] = datetime.strptime(d['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
    except Exception:
        # If parse fails, keep raw string (you can log this)
        pass
    d['status'] = int(d['status'])
    return d

def load_and_parse_from_zip(zip_path, filename_inside_zip):
    rows = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(filename_inside_zip, 'r') as f:
            # decode lines; file might be large so iterate line by line
            for raw in f:
                line = raw.decode('utf-8', errors='replace').strip()
                if not line:
                    continue
                parsed = parse_line(line)
                if parsed:
                    rows.append(parsed)
                else:
                    # Optionally collect malformed lines or count them
                    # malformed_lines.append(line)
                    pass
    df = pd.DataFrame(rows)
    # convert timestamp to pandas datetime (if not already)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    return df

if __name__ == "__main__":
    df = load_and_parse_from_zip(zip_path, log_filename_inside_zip)
    print("Parsed rows:", len(df))
    print(df.head(10))
    # Save to CSV for later analysis if you want
    df.to_csv("parsed_apache_logs.csv", index=False)
