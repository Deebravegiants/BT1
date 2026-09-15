# [H] Home Assistant: iOS Companion app forwards NFC/QR tag scans without confirmation, enabling silent automation execution

## Summary
Severity: High
Advisory: CVE-2026-66061
Aliases: GHSA-j23v-9672-677j
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-66061
Type: osv

## Details
Home Assistant is open source home automation software focused on local control and privacy.  Prior to 2026.5.0, the iOS Companion app treats tag links (NFC or QR) delivered through an OS-level routing mechanism such as iOS universal links as if they were physically scanned, without validating the calling app or prompting the user. As a result, any untrusted app on the device can forward an arbitrary tag to Home Assistant, causing it to execute the associated automation as though a legitimate user had scanned an authorized tag. This allows silent, unattended automation execution by untrusted local callers. This issue has been fixed in version 2026.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66061.json
- https://github.com/home-assistant/core/security/advisories/GHSA-j23v-9672-677j
- https://nvd.nist.gov/vuln/detail/CVE-2026-66061
- https://github.com/home-assistant/iOS/commit/45e05e6666c74fdbea44cc4d6fb103043fff6fd9
