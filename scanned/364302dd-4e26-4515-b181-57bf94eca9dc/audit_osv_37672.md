# [M] PX4 autopilot has a stack buffer overflow in tattu_can due to unbounded memcpy in frame assembly loop

## Summary
Severity: Medium
Advisory: CVE-2026-32707
Aliases: GHSA-wxwm-xmx9-hr32
CVSS: 5.2 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32707
Type: osv

## Details
PX4 autopilot is a flight control solution for drones. Prior to 1.17.0-rc2, tattu_can contains an unbounded memcpy in its multi-frame assembly loop, allowing stack memory overwrite when crafted CAN frames are processed. In deployments where tattu_can is enabled and running, a CAN-injection-capable attacker can trigger a crash (DoS) and memory corruption. This vulnerability is fixed in 1.17.0-rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32707.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-wxwm-xmx9-hr32
- https://nvd.nist.gov/vuln/detail/CVE-2026-32707
