# [M] CVE-2024-24254

## Summary
Severity: Medium
Advisory: CVE-2024-24254
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-24254
Type: osv

## Details
PX4 Autopilot 1.14 and earlier, due to the lack of synchronization mechanism for loading geofence data, has a Race Condition vulnerability in the geofence.cpp and mission_feasibility_checker.cpp. This will result in the drone uploading overlapping geofences and mission routes.

## References
- https://github.com/Drone-Lab/PX4-Autopilot/blob/report-can-not-pause-vulnerability/Multi-Threaded%20Race%20Condition%20bug%20found%20in%20PX4%20cause%20drone%20can%20not%20PAUSE.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24254.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24254
- https://github.com/PX4/PX4-Autopilot
