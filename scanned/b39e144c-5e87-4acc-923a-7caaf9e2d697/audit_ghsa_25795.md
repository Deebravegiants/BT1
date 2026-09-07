# [M] Possible filesystem space exhaustion by local users

## Summary
Severity: Medium
Advisory: GHSA-chxf-fjcf-7fwp
Ecosystem: Go
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-chxf-fjcf-7fwp
Type: github-advisory

## Affected
- Go: `github.com/google/fscrypt` — affected >=0 <0.3.3

## Details
`fscrypt` through v0.3.2 creates a world-writable directory by default when setting up a filesystem, allowing unprivileged users to exhaust filesystem space. We recommend upgrading to `fscrypt` v0.3.3 or above and adjusting the permissions on existing `fscrypt` metadata directories where applicable.

For more details, see [CVE-2022-25326](https://www.cve.org/CVERecord?id=CVE-2022-25326) and https://github.com/google/fscrypt#setting-up-fscrypt-on-a-filesystem.

## References
- https://github.com/google/fscrypt/security/advisories/GHSA-chxf-fjcf-7fwp
- https://github.com/google/fscrypt
