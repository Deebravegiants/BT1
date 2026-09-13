# [H] Home Assistant: Unconfirmed NFC/QR tag scans allow silent automation execution by untrusted callers

## Summary
Severity: High
Advisory: CVE-2026-66060
Aliases: GHSA-2xqv-hwrf-983f
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-66060
Type: osv

## Details
Home Assistant is open source home automation software focused on local control and privacy.  Prior to 2026.5.3,  the Companion app treats tag links (NFC or QR) delivered through an OS-level routing mechanism as if they were physically scanned, without validating the calling app or prompting the user. As a result, any untrusted app on the device can forward an arbitrary tag to Home Assistant, causing it to execute the associated automation as though a legitimate user had scanned an authorized tag. This allows silent, unattended automation execution by untrusted local callers. This issue is fixed in version 2026.8.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66060.json
- https://github.com/home-assistant/core/security/advisories/GHSA-2xqv-hwrf-983f
- https://nvd.nist.gov/vuln/detail/CVE-2026-66060
- https://github.com/home-assistant/android/commit/968b49c58e4eba4d06371a3f6e73198ec6c8d4a7
