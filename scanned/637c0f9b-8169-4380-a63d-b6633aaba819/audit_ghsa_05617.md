# [H] Bagisto SSTI vulnerability in type parameter can lead to RCE

## Summary
Severity: High
Advisory: GHSA-9hvg-qw5q-wqwp
CVE: CVE-2026-21450
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-9hvg-qw5q-wqwp
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <2.3.10

## Details
### Summary
SSTI is possible in Bagisto via type parameter can lead to RCE and other exploitations.

### Details
1. Go to `http://127.0.0.1:8000/admin/reporting/products/view?type={{7*7}}`

<img width="1251" height="282" alt="image" src="https://github.com/user-attachments/assets/652e96f4-631e-4322-8561-63f4d897a480" />


### Impact
Can lead to RCE, command injection.

## References
- https://github.com/bagisto/bagisto/security/advisories/GHSA-9hvg-qw5q-wqwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-21450
- https://github.com/bagisto/bagisto/commit/3f294b4837595929107d9c1bbd6d5b1222ef9fea
- https://github.com/bagisto/bagisto
- https://github.com/bagisto/bagisto/releases/tag/v2.3.10
