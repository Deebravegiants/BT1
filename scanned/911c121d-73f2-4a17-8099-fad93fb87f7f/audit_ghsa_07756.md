# [H] CleverTap Web SDK is vulnerable to DOM-based Cross-Site Scripting (XSS) via window.postMessage

## Summary
Severity: High
Advisory: GHSA-jfrq-hj9f-c8qx
CVE: CVE-2026-26862
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-jfrq-hj9f-c8qx
Type: github-advisory

## Affected
- npm: `clevertap-web-sdk` — affected >=0 <1.15.3

## Details
CleverTap Web SDK version 1.15.2 and earlier is vulnerable to DOM-based Cross-Site Scripting (XSS) via window.postMessage in the Visual Builder module. The origin validation in src/modules/visualBuilder/pageBuilder.js (lines 56-60) uses the includes() method to verify the originUrl contains "dashboard.clevertap.com", which can be bypassed by an attacker using a crafted subdomain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26862
- https://github.com/CleverTap/clevertap-web-sdk/issues/442
- https://github.com/CleverTap/clevertap-web-sdk/pull/417
- https://github.com/CleverTap/clevertap-web-sdk/commit/766f75f0c9082a27eb0b59c9fa4b0d9b19ba3d10
- https://github.com/CleverTap/clevertap-web-sdk/commit/84695b726a751614ddc3a4f71382c239c5833e03
- https://github.com/CleverTap/clevertap-web-sdk
- https://github.com/CleverTap/clevertap-web-sdk/blob/cf1b65d/src/modules/visualBuilder/pageBuilder.js#L56-L60
