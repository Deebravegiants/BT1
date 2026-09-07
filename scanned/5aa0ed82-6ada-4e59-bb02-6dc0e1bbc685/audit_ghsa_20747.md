# [M] Kirby CMS 2.5.12 Cross-site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-c7x2-7h8r-jq4m
CVE: CVE-2018-14519
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-08-25
Source: https://github.com/advisories/GHSA-c7x2-7h8r-jq4m
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0

## Details
An issue was discovered in Kirby 2.5.12. The delete page functionality suffers from a CSRF flaw. A remote attacker can craft a malicious CSRF page and force the user to delete a page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14519
- https://github.com/getkirby/kirby
- https://www.exploit-db.com/exploits/45090
- http://zaranshaikh.blogspot.com
