# [H] CVE-2026-26742

## Summary
Severity: High
Advisory: CVE-2026-26742
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-26742
Type: osv

## Details
PX4 Autopilot versions 1.12.x through 1.15.x contain a protection mechanism failure in the "Re-arm Grace Period" logic. The system incorrectly applies the in-air emergency re-arm logic to ground scenarios. If a pilot switches to Manual mode and re-arms within 5 seconds (default configuration) of an automatic landing, the system bypasses all pre-flight safety checks, including the throttle threshold check. This allows for an immediate high-thrust takeoff if the throttle stick is raised, leading to loss of control.

## References
- https://github.com/npuwyw/PX4-Autopilot/blob/audit-v1.12.3-mode-transition-logic-flaw/PX4_Autopilot_Mode_Switching_Logic_Vulnerability.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26742.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26742
