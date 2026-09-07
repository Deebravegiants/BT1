# [M] Cross Site Request Forgery in firefly-iii 

## Summary
Severity: Medium
Advisory: GHSA-hjhp-hwfj-hwf3
CVE: CVE-2021-4005
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-hjhp-hwfj-hwf3
Type: github-advisory

## Affected
- Packagist: `grumpydictator/firefly-iii` — affected >=0 <5.6.5

## Details
firefly-iii is vulnerable to a Cross-Site Request Forgery (CSRF) attack which can disable two factor authentication for the target user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4005
- https://github.com/firefly-iii/firefly-iii/commit/03a1601bf343181df9f405dd2109aec483cb7053
- https://github.com/firefly-iii/firefly-iii
- https://huntr.dev/bounties/bf4ef581-325a-492d-a710-14fcb53f00ff
