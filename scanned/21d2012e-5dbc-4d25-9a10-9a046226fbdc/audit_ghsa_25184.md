# [H] Pimcore CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-gmff-vcv6-mmfr
CVE: CVE-2018-14057
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gmff-vcv6-mmfr
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <5.3.0

## Details
Pimcore before 5.3.0 allows remote attackers to conduct cross-site request forgery (CSRF) attacks by leveraging validation of the `X-pimcore-csrf-token` anti-CSRF token only in the "Settings > Users / Roles" function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14057
- https://www.exploit-db.com/exploits/45208
- https://www.sec-consult.com/en/blog/advisories/sql-injection-xss-csrf-vulnerabilities-in-pimcore-software
- http://packetstormsecurity.com/files/148954/Pimcore-5.2.3-CSRF-Cross-Site-Scripting-SQL-Injection.html
- http://seclists.org/fulldisclosure/2018/Aug/13
