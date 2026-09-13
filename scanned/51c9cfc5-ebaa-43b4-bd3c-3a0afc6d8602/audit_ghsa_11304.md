# [M] go-git: Maliciously crafted idx file can cause asymmetric memory consumption

## Summary
Severity: Medium
Advisory: GHSA-jhf3-xxhw-2wpp
CVE: CVE-2026-34165
CWE: CWE-191, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-jhf3-xxhw-2wpp
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-git/v5` — affected >=5.0.0 <5.17.1

## Details
### Impact

A vulnerability has been identified in which a maliciously crafted `.idx` file can cause asymmetric memory consumption, potentially exhausting available memory and resulting in a Denial of Service (DoS) condition.

Exploitation requires write access to the local repository's `.git` directory, it order to create or alter existing `.idx` files. 

### Patches

Users should upgrade to `v5.17.1`, or the latest `v6` [pseudo-version](https://go.dev/ref/mod#pseudo-versions), in order to mitigate this vulnerability.

### Credit

The go-git maintainers thank @kq5y for finding and reporting this issue privately to the `go-git` project.

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-jhf3-xxhw-2wpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34165
- https://github.com/go-git/go-git
- https://github.com/go-git/go-git/releases/tag/v5.17.1
