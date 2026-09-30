# [M] lakeFS allows an authenticated user to cause a crash by exhausting server memory

## Summary
Severity: Medium
Advisory: GHSA-j7jw-28jm-whr6
CVE: CVE-2025-27100
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-21
Source: https://github.com/advisories/GHSA-j7jw-28jm-whr6
Type: github-advisory

## Affected
- Go: `github.com/treeverse/lakefs` — affected >=0 <1.50.0

## Details
### Impact

An authenticated user can crash lakeFS by exhausting server memory.  This is an authenticated denial-of-service issue.

### Patches
This problem has been patched and exists in versions 1.49.1 and below

### Workarounds

On S3 backends, configure
```yaml
# ...
blockstore:
  s3:
    disable_pre_signed_multipart: true
```
or set environment variable `LAKEFS_BLOCKSTORE_S3_DISABLE_PRE_SIGNED_MULTIPART` to `true`.

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/treeverse/lakeFS/security/advisories/GHSA-j7jw-28jm-whr6
- https://nvd.nist.gov/vuln/detail/CVE-2025-27100
- https://github.com/treeverse/lakeFS/commit/3a625752acdf3f8e137bec20451e71d0f9fa82f2
- https://github.com/treeverse/lakeFS
