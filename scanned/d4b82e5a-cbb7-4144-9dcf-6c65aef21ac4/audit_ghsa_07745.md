# [H] CleverTap Web SDK  is vulnerable to DOM-based XSS via handleCustomHtmlPreviewPostMessageEvent function

## Summary
Severity: High
Advisory: GHSA-j5mf-6rh3-rhgg
CVE: CVE-2026-26861
CWE: CWE-346, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-j5mf-6rh3-rhgg
Type: github-advisory

## Affected
- npm: `clevertap-web-sdk` — affected >=0 <1.15.3

## Details
CleverTap Web SDK version 1.15.2 and earlier is vulnerable to Cross-site Scripting (XSS) via window.postMessage. The handleCustomHtmlPreviewPostMessageEvent function in src/util/campaignRender/nativeDisplay.js performs insufficient origin validation using the includes() method, which can be bypassed by an attacker using a subdomain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26861
- https://github.com/CleverTap/clevertap-web-sdk/issues/424
- https://github.com/CleverTap/clevertap-web-sdk/pull/417
- https://github.com/CleverTap/clevertap-web-sdk/commit/84695b726a751614ddc3a4f71382c239c5833e03
- https://github.com/CleverTap/clevertap-web-sdk
- https://github.com/CleverTap/clevertap-web-sdk/blob/cf1b65d/src/util/campaignRender/nativeDisplay.js#L118-L121
