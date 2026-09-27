# [M] Fleet Vulnerable to Windows MDM cross-device command disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-34391
Aliases: GHSA-wg7j-pcc3-h4rh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-34391
Type: osv

## Details
Fleet is open source device management software. Prior to 4.81.1, a vulnerability in Fleet's Windows MDM command processing allows a malicious enrolled device to access MDM commands intended for other devices, potentially exposing sensitive configuration data such as WiFi credentials, VPN secrets, and certificate payloads across the entire Windows fleet. Version 4.81.1 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34391.json
- https://github.com/fleetdm/fleet/security/advisories/GHSA-wg7j-pcc3-h4rh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34391
