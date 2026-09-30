# [H] PX4 autopilot has a global buffer overflow in crsf_rc via oversized variable-length known packet

## Summary
Severity: High
Advisory: CVE-2026-32706
Aliases: GHSA-mqgj-hh4g-fg5p
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32706
Type: osv

## Details
PX4 autopilot is a flight control solution for drones. Prior to 1.17.0-rc2, The crsf_rc parser accepts an oversized variable-length known packet and copies it into a fixed 64-byte global buffer without a bounds check. In deployments where crsf_rc is enabled on a CRSF serial port, an adjacent/raw-serial attacker can trigger memory corruption and crash PX4. This vulnerability is fixed in 1.17.0-rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32706.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-mqgj-hh4g-fg5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-32706
