# [H] Home Assistant: Cross-origin iframe access token exfiltration via WebView JS bridge callback injection

## Summary
Severity: High
Advisory: CVE-2026-44698
Aliases: GHSA-7jp2-p2fw-mgvf
CVSS: 8.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44698
Type: osv

## Details
Home Assistant is open source home automation software that puts local control and privacy first. Prior to 2026.4.1 for iOS and 2026.4.4 for Android, he Home Assistant Companion apps for Android and iOS expose a JavaScript bridge to the in-app WebView window.externalApp on Android and webkit.messageHandlers.getExternalAuth (alongside revokeExternalAuth and externalBus) on iOS. Two flaws expose the bridge to all frames (including cross-origin iframes) and unsanitized interpolation of the JavaScript callback identifier allows a cross-origin iframe rendered inside the Companion app to execute arbitrary JavaScript in the Home Assistant frontend's main-frame origin and exfiltrate the signed-in user's access token. This vulnerability is fixed in 2026.4.1 for iOS and 2026.4.4 for Android.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44698.json
- https://github.com/home-assistant/core/security/advisories/GHSA-7jp2-p2fw-mgvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44698
