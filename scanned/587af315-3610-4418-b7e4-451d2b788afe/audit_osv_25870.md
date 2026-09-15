# [M] PX4-Autopilot Heap Buffer Overflow Bug

## Summary
Severity: Medium
Advisory: CVE-2023-46256
Aliases: GHSA-5hvv-q2r5-rppw
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:N/A:L)
Published: 2023-10-31
Source: https://osv.dev/vulnerability/CVE-2023-46256
Type: osv

## Details
PX4-Autopilot provides PX4 flight control solution for drones. In versions 1.14.0-rc1 and prior, PX4-Autopilot has a heap buffer overflow vulnerability in the parser function due to the absence of `parserbuf_index` value checking. A malfunction of the sensor device can cause a heap buffer overflow with leading unexpected drone behavior. Malicious applications can exploit the vulnerability even if device sensor malfunction does not occur. Up to the maximum value of an `unsigned int`, bytes sized data can be written to the heap memory area. As of time of publication, no fixed version is available.

## References
- https://github.com/PX4/PX4-Autopilot/blob/main/src/drivers/distance_sensor/lightware_laser_serial/parser.cpp#L87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46256.json
- https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-5hvv-q2r5-rppw
- https://nvd.nist.gov/vuln/detail/CVE-2023-46256
