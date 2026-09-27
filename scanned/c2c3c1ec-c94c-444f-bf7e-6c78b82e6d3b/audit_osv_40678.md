# [H] Home Assistant: Exported BroadcastReceiver allows local apps to spoof device location

## Summary
Severity: High
Advisory: CVE-2026-54318
Aliases: GHSA-77r5-pw5w-mgj3
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-54318
Type: osv

## Details
Home Assistant is open source home automation software that puts local control and privacy first. Prior to 2026.5.3, the LocationSensorManager BroadcastReceiver is exported with no permission. Any installed app, with zero runtime permissions, can broadcast a forged Google Play Services LocationResult directly to it; the receiver trusts the extra and forwards it to the user's Home Assistant server as the device's real location. This bypasses Android's developer-mode "Mock Location" gate and allows a local malicious app to drive zone-based automations (unlock door / disarm alarm / open garage) by faking the user's GPS position. This vulnerability is fixed in 2026.5.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54318.json
- https://github.com/home-assistant/core/security/advisories/GHSA-77r5-pw5w-mgj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-54318
- https://github.com/home-assistant/android/pull/6837
