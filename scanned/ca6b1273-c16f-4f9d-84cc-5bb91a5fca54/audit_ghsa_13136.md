# [H] Minio vulnerable to Privilege Escalation on Windows via Path separator manipulation

## Summary
Severity: High
Advisory: GHSA-w23q-4hw3-2pp6
CVE: CVE-2023-28433
CWE: CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-w23q-4hw3-2pp6
Type: github-advisory

## Affected
- Go: `github.com/minio/minio` — affected >=0 <0.0.0-202303200735

## Details
### Impact
All users on Windows are impacted. MinIO fails to filter the `\` character, which allows for arbitrary object placement across
buckets. As a result, a user with low privileges, such as an access key, service account, or STS credential, which only has permission to `PutObject` in a specific bucket, can create an admin user.

### Patches
There are two patches that fix this problem comprehensively

```
commit b3c54ec81e0a06392abfb3a1ffcdc80c6fbf6ebc
Author: Harshavardhana <harsha@minio.io>
Date:   Mon Mar 20 13:16:00 2023 -0700

    reject object names with '\' on windows (#16856)
```

```
commit 8d6558b23649f613414c8527b58973fbdfa4d1b8
Author: Harshavardhana <harsha@minio.io>
Date:   Mon Mar 20 00:35:25 2023 -0700

    fix: convert '\' to '/' on windows (#16852)
```

### Workarounds
There are no known workarounds

### References
The vulnerable code:
```go
// minio/cmd/generic-handlers.go
// Check if the incoming path has bad path components,
// such as ".." and "."
// SlashSeparator -> /
// dotdotComponent -> ..
// dotComponent -> .
func hasBadPathComponent(path string) bool {
  path = strings.TrimSpace(path)
  for _, p := range strings.Split(path, SlashSeparator) {
    switch strings.TrimSpace(p) {
    case dotdotComponent:
      return true
    case dotComponent:
      return true
    }
  }
  return false
}
```

## References
- https://github.com/minio/minio/security/advisories/GHSA-w23q-4hw3-2pp6
- https://nvd.nist.gov/vuln/detail/CVE-2023-28433
- https://github.com/minio/minio/commit/8d6558b23649f613414c8527b58973fbdfa4d1b8
- https://github.com/minio/minio/commit/b3c54ec81e0a06392abfb3a1ffcdc80c6fbf6ebc
- https://github.com/minio/minio
- https://github.com/minio/minio/releases/tag/RELEASE.2023-03-20T20-16-18Z
