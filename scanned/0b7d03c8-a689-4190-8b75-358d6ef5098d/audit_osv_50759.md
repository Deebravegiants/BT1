# [C] CVE-2020-36969

## Summary
Severity: Critical
Advisory: CVE-2020-36969
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2020-36969
Type: osv

## Details
M/Monit 3.7.4 contains a privilege escalation vulnerability that allows authenticated users to modify user permissions by manipulating the admin parameter. Attackers can send a POST request to the /api/1/admin/users/update endpoint with a crafted payload to grant administrative access to a standard user account.

## References
- https://mmonit.com/
- https://www.vulncheck.com/advisories/mmonit-privilege-escalation
- https://www.exploit-db.com/exploits/49080
