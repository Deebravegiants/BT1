# [M] Enhanced Image plugin for CKEditor is vulnerable to Cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-g78h-pf65-46rv
CVE: CVE-2018-9861
CWE: CWE-79
Ecosystem: Packagist, npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g78h-pf65-46rv
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.5.0 <8.5.2
- npm: `ckeditor-dev` — affected >=4.5.10 <4.9.2
- Packagist: `drupal/core` — affected >=8.0 <8.4.7
- Packagist: `drupal/drupal` — affected >=8.0 <8.4.7
- Packagist: `drupal/drupal` — affected >=8.5 <8.5.2

## Details
The Enhanced Image (aka [image2](https://github.com/ckeditor/ckeditor4/tree/master/plugins/image2)) plugin for CKEditor in versions 4.5.10 through 4.9.1; fixed in 4.9.2, and as used in Drupal 8 before 8.4.7 and 8.5.x before 8.5.2 and other products, is vulnerable to cross-site scripting because it allows remote attackers to inject arbitrary web script through a crafted IMG element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-9861
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2018-9861.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2018-9861.yaml
- https://github.com/ckeditor/ckeditor-dev/blob/master/CHANGES.md
- https://www.drupal.org/sa-core-2018-003
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://www.securityfocus.com/bid/103924
