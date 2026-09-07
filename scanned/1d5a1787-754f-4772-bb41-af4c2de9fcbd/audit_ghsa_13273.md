# [C] CleverTap Cordova plugin vulnerable to Cross-site Scripting

## Summary
Severity: Critical
Advisory: GHSA-x2ph-qqwm-9cc6
CVE: CVE-2023-2507
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-15
Source: https://github.com/advisories/GHSA-x2ph-qqwm-9cc6
Type: github-advisory

## Affected
- npm: `clevertap-cordova` — affected >=0 <2.7.0

## Details
CleverTap Cordova Plugin version 2.6.2 allows a remote attacker to execute JavaScript code in any application that is opened via a specially constructed deeplink by an attacker.

This is possible because the plugin does not correctly validate the data coming from the deeplinks before using them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2507
- https://fluidattacks.com/advisories/maiden
- https://github.com/CleverTap/clevertap-cordova
- https://github.com/CleverTap/clevertap-cordova/releases/tag/2.7.0
