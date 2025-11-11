import re
import pandas as pd
import matplotlib.pyplot as plt

# --- Step 1: Load and parse the log file ---
log_pattern = re.compile(
    r'(?P<host>\S+) - - \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<resource>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\S+) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
)

rows = []
with open("apache_logs.txt", "r", encoding="utf-8") as f:
    for line in f:
        match = log_pattern.match(line)
        if match:
            row = match.groupdict()
            row['size'] = int(row['size']) if row['size'].isdigit() else 0
            rows.append(row)

df = pd.DataFrame(rows)
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%b/%Y:%H:%M:%S %z')
print("Parsed rows:", len(df))

# --- Step 2: Basic Statistical Queries ---
# a) Total number of requests
total_requests = len(df)
print("Total number of requests:", total_requests)

# b) Number of unique hosts
unique_hosts = df['host'].nunique()
print("Number of unique hosts:", unique_hosts)

# c) Requests per day
df['date'] = df['timestamp'].dt.date
requests_per_day = df.groupby('date').size()
print("Requests per day:")
print(requests_per_day)

# Optional: visualize requests per day
requests_per_day.plot(kind='bar', figsize=(10,5), title='Requests per Day')
plt.xlabel('Date')
plt.ylabel('Number of Requests')
plt.tight_layout()
plt.show()

# d) Total data transferred
total_data = df['size'].sum()
total_data_mb = total_data / (1024 * 1024)
print("Total data transferred (bytes):", total_data)
print("Total data transferred (MB):", round(total_data_mb, 2))


# --- Step 3: Error and Performance Analysis ---

# a) Count the number of 404 errors
errors_404 = df[df['status'] == '404']
num_404 = len(errors_404)
print("\nNumber of 404 errors:", num_404)

# b) List all distinct HTTP status codes and their frequencies
status_counts = df['status'].value_counts().sort_index()
print("\nHTTP Status Code Counts:")
print(status_counts)

# Optional: visualize as a bar chart
status_counts.plot(kind='bar', figsize=(8,5), title='HTTP Status Code Distribution')
plt.xlabel('Status Code')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# c) Identify days with the highest number of 404 errors
if not errors_404.empty:
    errors_404_per_day = errors_404.groupby('date').size().sort_values(ascending=False)
    print("\n404 Errors per Day:")
    print(errors_404_per_day)

    # visualize 404s per day
    errors_404_per_day.plot(kind='bar', figsize=(8,5), title='404 Errors per Day', color='orange')
    plt.xlabel('Date')
    plt.ylabel('Number of 404 Errors')
    plt.tight_layout()
    plt.show()
else:
    print("\nNo 404 errors found in the dataset.")

# --- 4: User Behavior Analysis ---

# a) Most frequently used HTTP methods
method_counts = df['method'].value_counts()
print("\nMost frequently used HTTP methods:")
print(method_counts)

# Optional: visualize
method_counts.plot(kind='bar', figsize=(6,4), title='HTTP Methods Frequency', color='skyblue')
plt.xlabel('HTTP Method')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# b) Top 10 most requested resources (URLs)
top_resources = df['resource'].value_counts().head(10)
print("\nTop 10 most requested resources:")
print(top_resources)

# Optional: visualize
top_resources.plot(kind='bar', figsize=(10,5), title='Top 10 Requested Resources', color='green')
plt.xlabel('Resource')
plt.ylabel('Number of Requests')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# c) Most active clients (IPs with most requests)
top_hosts = df['host'].value_counts().head(10)
print("\nTop 10 most active clients (IP addresses):")
print(top_hosts)

# Optional: visualize
top_hosts.plot(kind='bar', figsize=(8,5), title='Top 10 Active Clients', color='orange')
plt.xlabel('IP Address')
plt.ylabel('Number of Requests')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# d) Identify peak hours of traffic during the day

# Extract the hour from the timestamp
df['hour'] = df['timestamp'].dt.hour

# Count number of requests per hour
requests_per_hour = df.groupby('hour').size()

print("\nRequests per hour:")
print(requests_per_hour)

# Find the hour with the highest traffic
peak_hour = requests_per_hour.idxmax()
peak_count = requests_per_hour.max()
print(f"\nPeak traffic occurs at hour {peak_hour}:00 with {peak_count} requests")

# Optional: visualize requests per hour
requests_per_hour.plot(kind='bar', figsize=(10,5), title='Requests per Hour')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Requests')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


# Ensure status is integer
df['status'] = df['status'].astype(int)

# Filter error requests
error_requests = df[df['status'] >= 400]

# Count errors per resource
errors_per_resource = error_requests['resource'].value_counts()

# Top resource(s) generating errors
print('Errors per resource:')
print(errors_per_resource.head(10))

print('Average response size per request type:')
avg_size_per_method = df.groupby('method')['size'].mean()
print(avg_size_per_method)

print('Server load patterns by hour')
df['hour'] = df['timestamp'].dt.hour
requests_per_hour = df.groupby('hour').size()
print(requests_per_hour)


requests_per_hour.plot(kind='bar', title='Server Load by Hour')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Requests')
plt.show()