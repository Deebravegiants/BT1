# [M] BuildKit vulnerable to possible panic when incorrect parameters sent from frontend

## Summary
Severity: Medium
Advisory: GHSA-9p26-698r-w4hx
CVE: CVE-2024-23650
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-9p26-698r-w4hx
Type: github-advisory

## Affected
- Go: `github.com/moby/buildkit` — affected >=0 <0.12.5

## Details
### Impact
A malicious BuildKit client or frontend could craft a request that could lead to BuildKit daemon crashing with a panic.

### Patches
The issue has been fixed in v0.12.5

### Workarounds
Avoid using BuildKit frontends from untrusted sources. A frontend image is usually specified as the `#syntax` line on your Dockerfile, or with `--frontend` flag when using `buildctl build` command. 

### References

## References
- https://github.com/moby/buildkit/security/advisories/GHSA-9p26-698r-w4hx
- https://nvd.nist.gov/vuln/detail/CVE-2024-23650
- https://github.com/moby/buildkit/pull/4601
- https://github.com/moby/buildkit/commit/481d9c45f473c58537f39694a38d7995cc656987
- https://github.com/moby/buildkit/commit/7718bd5c3dc8fc5cd246a30cc41766e7a53c043c
- https://github.com/moby/buildkit/commit/83edaef59d545b93e2750f1f85675a3764593fee
- https://github.com/moby/buildkit/commit/96663dd35bf3787d7efb1ee7fd9ac7fe533582ae
- https://github.com/moby/buildkit/commit/e1924dc32da35bfb0bfdbb9d0fc7bca25e552330
- https://github.com/moby/buildkit
- https://github.com/moby/buildkit/releases/tag/v0.12.5
