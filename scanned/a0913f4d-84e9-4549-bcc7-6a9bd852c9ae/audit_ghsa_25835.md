# [M] Possible privilege escalation via bash completion script

## Summary
Severity: Medium
Advisory: GHSA-w4f8-fxq2-j35v
Ecosystem: Go
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-w4f8-fxq2-j35v
Type: github-advisory

## Affected
- Go: `github.com/google/fscrypt` — affected >=0 <0.3.3

## Details
The bash completion script for `fscrypt` through v0.3.2 allows injection of commands via crafted mountpoint paths, allowing privilege escalation under a specific set of circumstances. A local user who has control over mountpoint paths could potentially escalate their privileges if they create a malicious mountpoint path and if the system administrator happens to be using the `fscrypt` bash completion script to complete mountpoint paths. We recommend upgrading to v0.3.3 or above.

For more details, see [CVE-2022-25328](https://www.cve.org/CVERecord?id=CVE-2022-25328).

## References
- https://github.com/google/fscrypt/security/advisories/GHSA-w4f8-fxq2-j35v
- github.com/google/fscrypt
