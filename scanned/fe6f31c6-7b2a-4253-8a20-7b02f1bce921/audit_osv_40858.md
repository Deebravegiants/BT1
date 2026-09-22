# [H] Home Assistant: iOS Companion App ignores internal SSID allowlist for connections – possible leak of access token and sensor data

## Summary
Severity: High
Advisory: CVE-2026-55844
Aliases: GHSA-cm5v-547m-qh5h
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-55844
Type: osv

## Details
Home Assistant is open source home automation software that puts local control and privacy first. Prior to 2025.5.0, The iOS companion app ignores the SSID allowlist for internal networks. The app uses SSID to detect when to use the internal URL, but whenever the app cannot find any other URL to be used, it fallbacks to the internal URL as well, which can expose user's token when connected to a not secure network. This vulnerability is fixed in 2025.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55844.json
- https://github.com/home-assistant/core/security/advisories/GHSA-cm5v-547m-qh5h
- https://nvd.nist.gov/vuln/detail/CVE-2026-55844
