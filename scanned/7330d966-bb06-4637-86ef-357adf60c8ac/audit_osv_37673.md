# [H] Zenoh uORB Subscriber Allows Arbitrary Stack Allocation (PX4/PX4-Autopilot)

## Summary
Severity: High
Advisory: CVE-2026-32708
Aliases: GHSA-69g4-hcqf-j45p
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32708
Type: osv

## Details
PX4 autopilot is a flight control solution for drones. Prior to 1.17.0-rc2, the Zenoh uORB subscriber allocates a stack VLA directly from the incoming payload length without bounds. A remote Zenoh publisher can send an oversized fragmented message to force an unbounded stack allocation and copy, causing a stack overflow and crash of the Zenoh bridge task. This vulnerability is fixed in 1.17.0-rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32708.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-69g4-hcqf-j45p
- https://nvd.nist.gov/vuln/detail/CVE-2026-32708
