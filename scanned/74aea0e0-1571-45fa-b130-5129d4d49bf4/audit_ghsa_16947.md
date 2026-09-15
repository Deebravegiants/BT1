# [M] Archiver Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rhh4-rh7c-7r5v
CVE: CVE-2024-0406
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-04-06
Source: https://github.com/advisories/GHSA-rhh4-rh7c-7r5v
Type: github-advisory

## Affected
- Go: `github.com/mholt/archiver/v3` — affected >=3.0.0
- Go: `github.com/mholt/archiver` — affected >=3.0.0

## Details
A flaw was discovered in the mholt/archiver package. This flaw allows an attacker to create a specially crafted tar file, which, when unpacked, may allow access to restricted files or directories. This issue can allow the creation or overwriting of files with the user's or application's privileges using the library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0406
- https://access.redhat.com/errata/RHSA-2025:2449
- https://access.redhat.com/security/cve/CVE-2024-0406
- https://bugzilla.redhat.com/show_bug.cgi?id=2257749
- https://github.com/mholt/archiver
- https://pkg.go.dev/vuln/GO-2024-2698
