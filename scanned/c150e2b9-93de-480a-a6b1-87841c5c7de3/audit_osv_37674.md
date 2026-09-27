# [M] PX4 Autopilot MAVLink FTP Unauthenticated Path Traversal (Arbitrary File Read/Write/Delete)

## Summary
Severity: Medium
Advisory: CVE-2026-32709
Aliases: GHSA-fh32-qxj9-x32f
CVSS: 5.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32709
Type: osv

## Details
PX4 autopilot is a flight control solution for drones. Prior to 1.17.0-rc2, An unauthenticated path traversal vulnerability in the PX4 Autopilot MAVLink FTP implementation allows any MAVLink peer to read, write, create, delete, and rename arbitrary files on the flight controller filesystem without authentication. On NuttX targets, the FTP root directory is an empty string, meaning attacker-supplied paths are passed directly to filesystem syscalls with no prefix or sanitization for read operations. On POSIX targets (Linux companion computers, SITL), the write-path validation function unconditionally returns true, providing no protection. A TOCTOU race condition in the write validation on NuttX further allows bypassing the only existing guard. This vulnerability is fixed in 1.17.0-rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32709.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-fh32-qxj9-x32f
- https://nvd.nist.gov/vuln/detail/CVE-2026-32709
