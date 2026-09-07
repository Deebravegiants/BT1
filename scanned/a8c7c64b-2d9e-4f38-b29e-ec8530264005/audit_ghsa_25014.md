# [M] User Plugin for October CSS Allows XSS

## Summary
Severity: Medium
Advisory: GHSA-x5jc-34xf-c24q
CVE: CVE-2018-10366
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x5jc-34xf-c24q
Type: github-advisory

## Affected
- Packagist: `rainlab/user-plugin` — affected >=0 <1.5.0

## Details
An issue was discovered in the Users (aka Front-end user management) plugin 1.4.5 for October CMS. XSS exists in the name field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10366
- https://github.com/rainlab/user-plugin/commit/098c2bc907443d67e9e18645f850e3de42941d20
- https://github.com/rainlab/user-plugin
- https://www.exploit-db.com/exploits/44546
