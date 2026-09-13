# [C] Privilege Escalation in cordova-plugin-inappbrowser

## Summary
Severity: Critical
Advisory: GHSA-c6pw-q7f2-97hv
CVE: CVE-2019-0219
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-c6pw-q7f2-97hv
Type: github-advisory

## Affected
- npm: `cordova-plugin-inappbrowser` — affected >=0 <3.1.0

## Details
Versions of `cordova-plugin-inappbrowser` prior to 3.1.0 are vulnerable to Privilege Escalation. A website running in the InAppBrowser webview on Android could execute arbitrary JavaScript in the main application's webview using a specially crafted gap-iab: URI. This affects Cordova Android applications using the package.


## Recommendation

Upgrade to version 3.1.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0219
- https://github.com/apache/cordova-plugin-inappbrowser
- https://lists.apache.org/thread.html/197482d5ab80c0bff4a5ec16e1b0466df38389d9a4b5331d777f14fc%40%3Cdev.cordova.apache.org%3E
- https://lists.apache.org/thread/4vtg0trdrh5203dktt4f3vkd5z2d5ndj
- https://www.npmjs.com/advisories/1467
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://www.openwall.com/lists/oss-security/2019/11/28/1
