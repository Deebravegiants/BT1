# [M] Fork CMS XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xcmj-xjhg-wvhq
CVE: CVE-2018-20682
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xcmj-xjhg-wvhq
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0

## Details
Fork CMS 5.0.6 allows stored XSS via the `private/en/settings` `facebook_admin_ids` parameter (aka "Admin ids" input in the Facebook section).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20682
- https://github.com/forkcms/forkcms
- https://www.netsparker.com/web-applications-advisories/ns-18-032-stored-cross-site-scripting-in-forkcms
