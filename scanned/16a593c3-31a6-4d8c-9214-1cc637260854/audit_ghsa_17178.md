# [M] Bagisto vulnerable to Insecure Direct Object Reference (IDOR)

## Summary
Severity: Medium
Advisory: GHSA-pmc7-hmmw-g96q
CVE: CVE-2023-36238
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-13
Source: https://github.com/advisories/GHSA-pmc7-hmmw-g96q
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <1.3.2

## Details
Insecure Direct Object Reference (IDOR) in Bagisto v.1.5.0 allows an attacker to obtain sensitive information via the invoice ID parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36238
- https://github.com/bagisto/bagisto/pull/4697
- https://github.com/bagisto/bagisto/commit/2a24098cb582e072c87177e0ad17be45f240ad17
- https://github.com/Ek-Saini/security/blob/main/IDOR-Bagisto
- https://github.com/bagisto/bagisto
