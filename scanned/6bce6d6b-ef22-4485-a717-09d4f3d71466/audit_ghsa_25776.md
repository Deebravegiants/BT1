# [M] Denial of service via insufficient metadata validation

## Summary
Severity: Medium
Advisory: GHSA-p93v-m2r2-4387
Ecosystem: Go
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-p93v-m2r2-4387
Type: github-advisory

## Affected
- Go: `github.com/google/fscrypt` — affected >=0 <0.3.3

## Details
The PAM module for `fscrypt` through v0.3.2 doesn't adequately validate `fscrypt` metadata files, allowing users to create malicious metadata files that prevent other users from logging in. A local user can cause a denial of service by creating a `fscrypt` metadata file that prevents other users from logging into the system. We recommend upgrading to v0.3.3 or above.

For more details, see [CVE-2022-25327](https://www.cve.org/CVERecord?id=CVE-2022-25327).

## References
- https://github.com/google/fscrypt/security/advisories/GHSA-p93v-m2r2-4387
- https://github.com/google/fscrypt/commit/91aa3ebf42032ca783c41f9ec25d885875f66ddb
- https://pkg.go.dev/vuln/GO-2022-0340
- github.com/google/fscrypt
