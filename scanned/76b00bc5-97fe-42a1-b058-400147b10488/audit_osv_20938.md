# [H] CVE-2021-38706

## Summary
Severity: High
Advisory: CVE-2021-38706
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-38706
Type: osv

## Details
messages_load.php in ClinicCases 7.3.3 suffers from a blind SQL injection vulnerability, which allows low-privileged attackers to execute arbitrary SQL commands through a vulnerable parameter.

## References
- https://cliniccases.com
- https://github.com/judsonmitchell/ClinicCases/releases
