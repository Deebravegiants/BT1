# [M] Incorrect Authorization in thinkcmf

## Summary
Severity: Medium
Advisory: GHSA-v25c-8349-v2q3
CVE: CVE-2021-40616
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-06-15
Source: https://github.com/advisories/GHSA-v25c-8349-v2q3
Type: github-advisory

## Affected
- Packagist: `thinkcmf/thinkcmf` — affected >=0 <6.0.0

## Details
thinkcmf v5.1.7 has an unauthorized vulnerability. The attacker can modify the password of the administrator account with id 1 through the background user management group permissions. The use condition is that the background user management group authority is required.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40616
- https://github.com/thinkcmf/thinkcmf/issues/722
- https://github.com/thinkcmf/thinkcmf
