# [M] Pimcore XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-276r-24xq-hwg8
CVE: CVE-2018-14059
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-276r-24xq-hwg8
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <5.3.0

## Details
Pimcore allows XSS via Users, Assets, Data Objects, Video Thumbnails, Image Thumbnails, Field-Collections, Objectbrick, Classification Store, Document Types, Predefined Properties, Predefined Asset Metadata, Quantity Value, and Static Routes functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14059
- https://www.exploit-db.com/exploits/45208
- https://www.sec-consult.com/en/blog/advisories/sql-injection-xss-csrf-vulnerabilities-in-pimcore-software
- http://packetstormsecurity.com/files/148954/Pimcore-5.2.3-CSRF-Cross-Site-Scripting-SQL-Injection.html
- http://seclists.org/fulldisclosure/2018/Aug/13
