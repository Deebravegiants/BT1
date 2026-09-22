# [H] A BOLA vulnerability in POST /appointments in EasyAppointments < 1.5.0

## Summary
Severity: High
Advisory: CVE-2023-3285
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2023-3285
Type: osv

## Details
A BOLA vulnerability in POST /appointments allows a low privileged user to create an appointment for any user in the system (including admin). This results in unauthorized data manipulation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3285.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3285
- https://github.com/alextselegidis/easyappointments
