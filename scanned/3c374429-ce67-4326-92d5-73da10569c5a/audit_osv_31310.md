# [M] AngularJS improper sanitization in 'srcset' attribute

## Summary
Severity: Medium
Advisory: CVE-2024-8372
Aliases: GHSA-m9gf-397r-hwpg
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-09-09
Source: https://osv.dev/vulnerability/CVE-2024-8372
Type: osv

## Details
Improper sanitization of the value of the 'srcset' attribute in AngularJS allows attackers to bypass common image source restrictions, which can also lead to a form of  Content Spoofing https://owasp.org/www-community/attacks/Content_Spoofing .

This issue affects AngularJS versions 1.3.0-rc.4 and greater.

Note:
The AngularJS project is End-of-Life and will not receive any updates to address this issue. For more information see  here https://docs.angularjs.org/misc/version-support-status .

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00005.html
- https://registry.npmjs.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8372.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8372
- https://security.netapp.com/advisory/ntap-20241122-0002/
- https://www.herodevs.com/vulnerability-directory/cve-2024-8372
- https://github.com/angular/angular.js
- https://codepen.io/herodevs/full/xxoQRNL/0072e627abe03e9cda373bc75b4c1017
