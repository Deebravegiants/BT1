# [M] The disqualify lead action may be executed without CSRF token check

## Summary
Severity: Medium
Advisory: GHSA-vf7h-6246-hm43
CVE: CVE-2021-39198
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-vf7h-6246-hm43
Type: github-advisory

## Affected
- Packagist: `oro/crm` — affected >=3.1.0 <4.1.17
- Packagist: `oro/crm` — affected >=4.2.0 <4.2.7

## Details
### Summary
The attacker is able to disqualify any Lead with a Cross-Site Request Forgery (CSRF) attack.

### Workarounds
There are no workarounds that address this vulnerability.

## References
- https://github.com/oroinc/crm/security/advisories/GHSA-vf7h-6246-hm43
- https://nvd.nist.gov/vuln/detail/CVE-2021-39198
- https://github.com/oroinc/crm
