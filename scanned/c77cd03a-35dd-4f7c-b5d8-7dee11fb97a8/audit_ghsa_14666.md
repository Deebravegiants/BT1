# [M] PGHoard Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m9hc-vxjj-4x6q
CVE: CVE-2024-56142
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-17
Source: https://github.com/advisories/GHSA-m9hc-vxjj-4x6q
Type: github-advisory

## Affected
- PyPI: `pghoard` — affected >=0 <2.6.1-rc

## Details
A vulnerability has been discovered that could allow an attacker to acquire disk access with privileges equivalent to those of pghoard, allowing for unintended path traversal.  Depending on the permissions/privileges assigned to pghoard, this could allow disclosure of sensitive information.

## References
- https://github.com/Aiven-Open/pghoard/security/advisories/GHSA-m9hc-vxjj-4x6q
- https://nvd.nist.gov/vuln/detail/CVE-2024-56142
- https://github.com/Aiven-Open/pghoard/commit/fe9947642cc73bcacf6d19b93eb98f442223fb47
- https://github.com/Aiven-Open/pghoard
