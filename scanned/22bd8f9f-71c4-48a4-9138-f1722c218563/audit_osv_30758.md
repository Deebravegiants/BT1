# [H] CVE-2024-56317

## Summary
Severity: High
Advisory: CVE-2024-56317
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-56317
Type: osv

## Details
In Matter (aka connectedhomeip or Project CHIP) through 1.4.0.0, the WriteAcl function deletes all existing ACL entries first, and then attempts to recreate them based on user input. If input validation fails during decoding, the process stops, and no entries are restored by access-control-server.cpp, i.e., a denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56317.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56317
- https://github.com/project-chip/connectedhomeip/issues/36535
