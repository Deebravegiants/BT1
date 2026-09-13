# [H] A BOLA vulnerability in GET, PUT, DELETE /categories/{categoryId} in EasyAppointments < 1.5.0.

## Summary
Severity: High
Advisory: CVE-2023-38047
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2023-38047
Type: osv

## Details
A BOLA vulnerability in GET, PUT, DELETE /categories/{categoryId} allows a low privileged user to fetch, modify or delete the category of any user (including admin). This results in unauthorized access and unauthorized data manipulation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38047.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-38047
- https://github.com/alextselegidis/easyappointments
