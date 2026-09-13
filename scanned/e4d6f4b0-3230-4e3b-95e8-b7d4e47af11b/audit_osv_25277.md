# [C] A BOLA vulnerability in POST /admins in EasyAppointments < 1.5.0

## Summary
Severity: Critical
Advisory: CVE-2023-3287
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2023-3287
Type: osv

## Details
A BOLA vulnerability in POST /admins allows a low privileged user to create a high privileged user (admin) in the system. This results in privilege escalation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3287.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3287
- https://github.com/alextselegidis/easyappointments
