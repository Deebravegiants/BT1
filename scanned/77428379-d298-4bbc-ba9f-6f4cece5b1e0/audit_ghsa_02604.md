# [H] Improper use of cryptographic key in wal-g

## Summary
Severity: High
Advisory: GHSA-vrmr-f2qh-3hhf
CVE: CVE-2021-38599
CWE: CWE-922
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-vrmr-f2qh-3hhf
Type: github-advisory

## Affected
- Go: `github.com/wal-g/wal-g` — affected >=0 <1.1

## Details
WAL-G before 1.1, when a non-libsodium build (e.g., one of the official binary releases published as GitHub Releases) is used, silently ignores the libsodium encryption key and uploads cleartext backups. This is arguably a Principle of Least Surprise violation because "the user likely wanted to encrypt all file activity."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38599
- https://github.com/wal-g/wal-g/pull/1062
- https://github.com/wal-g/wal-g/commit/cadf598e1c2a345915a21a44518c5a4d5401e2e3
- https://github.com/wal-g/wal-g
- https://github.com/wal-g/wal-g/releases/tag/v1.1
