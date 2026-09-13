# [H] MCU Firmware Update Authentication Bypass on Caliptra Core

## Summary
Severity: High
Advisory: CVE-2026-5818
Aliases: GHSA-456r-gcjr-6rxq
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-5818
Type: osv

## Details
Incorrect check of function return value in Caliptra Core Runtime Firmware (ActivateFirmwareCmd::activate_fw modules) allows bypass of Caliptra Core's verification of the MCU FW during a hitless update.

This issue affects Core Runtime Firmware: from 2.0.0 through 2.0.1, 2.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5818.json
- https://github.com/chipsalliance/caliptra-sw/security/advisories/GHSA-456r-gcjr-6rxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-5818
- https://github.com/chipsalliance/caliptra-sw
