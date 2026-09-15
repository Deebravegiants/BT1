# [H] HashBrown CMS Directory Traversal

## Summary
Severity: High
Advisory: GHSA-q7hx-mrv5-6mrp
CVE: CVE-2020-5840
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q7hx-mrv5-6mrp
Type: github-advisory

## Affected
- npm: `hashbrown-cms` — affected >=0 <1.3.2

## Details
An issue was discovered in HashBrown CMS before 1.3.2. `Server/Entity/Resource/Connection.js` allows an attacker to reach a parent directory via a crafted name or ID field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5840
- https://github.com/HashBrownCMS/hashbrown-cms/commit/6b37b73944447bb29c6aaeb086b04196d80c692a
- https://github.com/HashBrownCMS/hashbrown-cms
- https://github.com/HashBrownCMS/hashbrown-cms/compare/v1.3.1...v1.3.2
- https://github.com/HashBrownCMS/hashbrown-cms/releases/tag/v1.3.2
