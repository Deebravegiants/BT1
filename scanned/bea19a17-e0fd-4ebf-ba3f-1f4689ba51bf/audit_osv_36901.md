# [H] CVE-2026-26741

## Summary
Severity: High
Advisory: CVE-2026-26741
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-26741
Type: osv

## Details
PX4 Autopilot versions 1.12.x through 1.15.x contain a logic flaw in the mode switching mechanism. When switching from Auto mode to Manual mode while the drone is in the "ARMED" state (after landing and before the automatic disarm triggered by the COM_DISARM_LAND parameter), the system lacks a throttle threshold safety check for the physical throttle stick. This flaw can directly cause the drone to lose control, experience rapid uncontrolled ascent (flyaway), and result in property damage

## References
- https://github.com/npuwyw/PX4-Autopilot/blob/audit-v1.12.3-mode-transition-logic-flaw/PX4_Autopilot_Mode_Switching_Logic_Vulnerability.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26741.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26741
