# [H] Marlin Firmware 2.1.2.7 Out-of-Bounds Write via M421 G-code Handler

## Summary
Severity: High
Advisory: CVE-2026-56111
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56111
Type: osv

## Details
Marlin Firmware through 2.1.2.7, fixed in commit 1f255d1, when built with MESH_BED_LEVELING enabled, contains an out-of-bounds write vulnerability in the M421 G-code handler that allows attackers to corrupt firmware memory by supplying out-of-range X and Y grid indices. Attackers can send a single crafted G-code command via USB serial, network interface, or malicious gcode file to write an attacker-controlled 32-bit float value past the z_values array bounds, corrupting adjacent firmware variables and causing denial of service or firmware state corruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56111
- https://www.vulncheck.com/advisories/marlin-firmware-out-of-bounds-write-via-m421-g-code-handler
- https://github.com/MarlinFirmware/Marlin/pull/28468
- https://github.com/MarlinFirmware/Marlin/commit/1f255d16ec2d456454fd444494cfb338d62b0fa1
- https://github.com/MarlinFirmware/Marlin
- https://github.com/MarlinFirmware/Marlin/issues/28467
