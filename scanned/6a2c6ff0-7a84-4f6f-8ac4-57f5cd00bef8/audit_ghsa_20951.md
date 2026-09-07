# [M] Craft CMS vulnerable to Cross-site Scripting via entry revisions and drafts

## Summary
Severity: Medium
Advisory: GHSA-mw37-wx8p-gp45
CVE: CVE-2022-37251
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-17
Source: https://github.com/advisories/GHSA-mw37-wx8p-gp45
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=3.7.0-beta.1 <3.7.55.2
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.2.1

## Details
Craft CMS `3.70-RC1`–`3.7.55.1` and `4.0.0-RC1`–`4.2.0.1` are vulnerable to Cross Site Scripting (XSS) via entry revisions and drafts. Versions `3.7.55.2` and `4.2.1` contain patches for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37251
- https://github.com/craftcms/cms/commit/7139213dbd9e177a3528aac8e2db8de91830f118
- https://github.com/craftcms/cms/commit/919c9074ff8596bf30a629b0888c529793e9a903
- https://github.com/craftcms/cms/commit/f0d9b8a1e3ac005a2418f7d3d9059b49a96e73ea
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#421---2022-08-09
- https://labs.integrity.pt/advisories/cve-2022-37251
- http://craft.com
