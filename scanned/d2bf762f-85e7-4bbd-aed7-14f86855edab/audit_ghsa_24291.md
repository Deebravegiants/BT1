# [H] Craft CMS Vulnerable to Server-Side Template Injection

## Summary
Severity: High
Advisory: GHSA-j7fx-v37j-v3w7
CVE: CVE-2018-20465
CWE: CWE-1336, CWE-311
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j7fx-v37j-v3w7
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=0

## Details
Craft CMS through 3.0.34 allows remote authenticated administrators to read sensitive information via server-side template injection, as demonstrated by a `{%` string for `craft.app.config.DB.user` and `craft.app.config.DB.password` in the URI Format of the Site Settings, which causes a cleartext username and password to be displayed in a URI field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20465
- https://github.com/phuctam/Server-Side-Template-Injection-in-CraftCMS-/issues/1
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/master/CHANGELOG-v3.md
