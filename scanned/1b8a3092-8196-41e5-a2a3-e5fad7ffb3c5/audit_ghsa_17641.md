# [M] AngularJS Incomplete Filtering of Special Elements vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4p4w-6hg8-63wx
CVE: CVE-2025-2336
CWE: CWE-791
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-4p4w-6hg8-63wx
Type: github-advisory

## Affected
- npm: `angular-sanitize` — affected >=1.3.1

## Details
Improper sanitization of the value of the 'href' and 'xlink:href' attributes in '<image>' SVG elements in AngularJS's 'ngSanitize' module allows attackers to bypass common image source restrictions. This can lead to a form of  Content Spoofing https://owasp.org/www-community/attacks/Content_Spoofing  and also negatively affect the application's performance and behavior by using too large or slow-to-load images.

This issue affects AngularJS versions greater than or equal to 1.3.1.

Note:
The AngularJS project is End-of-Life and will not receive any updates to address this issue. For more information see  here https://docs.angularjs.org/misc/version-support-status .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2336
- https://codepen.io/herodevs/pen/bNGYaXx/412a3a4218387479898912f60c269c6c
- https://github.com/angular/angular.js
- https://lists.debian.org/debian-lts-announce/2025/07/msg00005.html
- https://www.herodevs.com/vulnerability-directory/cve-2025-2336
- https://www.herodevs.com/vulnerability-directory/cve-2025-2336?angularjs-nes
