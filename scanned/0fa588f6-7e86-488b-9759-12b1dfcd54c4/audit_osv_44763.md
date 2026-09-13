# [M] PX4 Autopilot through 1.17.0 Use-After-Free via Temperature Calibration Task Startup

## Summary
Severity: Medium
Advisory: CVE-2026-86096
CVSS: 6.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-86096
Type: osv

## Details
PX4 Autopilot through 1.17.0 contains a use-after-free vulnerability in TemperatureCalibration::start() due to a race condition between task spawning and object deletion. Attackers can trigger the calibration process via shell commands to write to freed heap memory, corrupting unrelated objects or allocator metadata and destabilizing heap operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86096.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86096
- https://www.vulncheck.com/advisories/px4-autopilot-through-1.17.0-use-after-free-via-temperature-calibration-task-startup
- https://github.com/PX4/PX4-Autopilot/commit/b182e523d154fe029a49b48bb5f9d3d6693bc6bb
- https://github.com/PX4/PX4-Autopilot/pull/28487
- https://github.com/PX4/PX4-Autopilot
- https://github.com/PX4/PX4-Autopilot/blob/v1.17.0/src/modules/temperature_compensation/temperature_calibration/task.cpp
