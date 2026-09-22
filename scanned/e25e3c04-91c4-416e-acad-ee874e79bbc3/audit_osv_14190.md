# [H] CVE-2018-7745

## Summary
Severity: High
Advisory: CVE-2018-7745
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-03-07
Source: https://osv.dev/vulnerability/CVE-2018-7745
Type: osv

## Details
An issue was discovered in Western Bridge Cobub Razor 0.7.2. Authentication is not required for /index.php?/install/installation/createuserinfo requests, resulting in account creation.

## References
- https://github.com/cobub/razor/issues/161
- https://www.exploit-db.com/exploits/44419/
