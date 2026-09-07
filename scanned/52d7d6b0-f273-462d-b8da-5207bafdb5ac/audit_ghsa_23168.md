# [H] Bolt Cross Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-3g6c-88pf-m46f
CVE: CVE-2019-10874
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3g6c-88pf-m46f
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected >=3.6.6 <3.6.7

## Details
Cross Site Request Forgery (CSRF) in the `bolt/upload` File Upload feature in Bolt CMS 3.6.6 allows remote attackers to execute arbitrary code by uploading a JavaScript file to include executable extensions in the `file/edit/config/config.yml` configuration file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10874
- https://github.com/bolt/bolt/pull/7768/commits/91187aef36363a870d60b0a3c1bf8507af34c9e4
- https://fgsec.net/from-csrf-to-rce-bolt-cms
- https://github.com/bolt/bolt
- https://www.exploit-db.com/exploits/46664
- http://packetstormsecurity.com/files/152429/Bolt-CMS-3.6.6-Cross-Site-Request-Forgery-Code-Execution.html
