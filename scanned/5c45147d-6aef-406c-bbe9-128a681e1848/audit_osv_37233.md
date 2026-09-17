# [H] CVE-2026-30075

## Summary
Severity: High
Advisory: CVE-2026-30075
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-30075
Type: osv

## Details
OpenAirInterface Version 2.2.0 has a Buffer Overflow vulnerability in processing UplinkNASTransport containing Authentication Response containing a NAS PDU with oversize response (For example 100 byte). The response is decoded by AMF and passed to the AUSF component for verification. AUSF crashes on receiving this oversize response. This can prohibit users from further registration and verification and can cause Denial of Services (DoS).

## References
- https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-ausf/-/issues?show=eyJpaWQiOiI2IiwiZnVsbF9wYXRoIjoib2FpL2NuNWcvb2FpLWNuNWctYXVzZiIsImlkIjo1NDE5fQ%3D%3D
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30075.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30075
- https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-ausf/-/issues/6
