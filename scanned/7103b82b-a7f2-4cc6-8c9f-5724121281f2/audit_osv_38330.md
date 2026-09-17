# [C] CVE-2026-38971

## Summary
Severity: Critical
Advisory: CVE-2026-38971
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-38971
Type: osv

## Details
ardupilot through Plane-4.6.3 was found to contain an out-of-bounds read issue in libraries/GCS_MAVLink/GCS_serial_control.cpp in GCS_MAVLINK::handle_serial_control().

## References
- https://gist.github.com/quart27219/6bfcc615f89fb493d02aad480704593b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38971.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38971
- https://github.com/ArduPilot/ardupilot/issues/32524
- https://github.com/ArduPilot/ardupilot/pull/32587
- https://github.com/ArduPilot/ardupilot
