# [C] HashBrown CMS RCE

## Summary
Severity: Critical
Advisory: GHSA-4gjv-5jjp-rcgh
CVE: CVE-2020-6948
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4gjv-5jjp-rcgh
Type: github-advisory

## Affected
- npm: `hashbrown-cms` — affected >=0 <1.3.4

## Details
A remote code execution issue was discovered in HashBrown CMS through 1.3.3. `Server/Entity/Deployer/GitDeployer.js` has a `Service.AppService.exec call` that mishandles the URL, repository, username, and password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-6948
- https://github.com/HashBrownCMS/hashbrown-cms/issues/326
- https://github.com/HashBrownCMS/hashbrown-cms/commit/ff95bbad391fb7111355c643cadc02fe8792d758
- https://github.com/HashBrownCMS/hashbrown-cms
