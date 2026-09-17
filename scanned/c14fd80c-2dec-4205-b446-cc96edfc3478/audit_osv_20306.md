# [H] CVE-2021-32756

## Summary
Severity: High
Advisory: CVE-2021-32756
Aliases: GHSA-32x4-vj4r-57rq
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2021-32756
Type: osv

## Details
ManageIQ is an open-source management platform. In versions prior to jansa-4, kasparov-2, and lasker-1, there is a flaw in the MiqExpression module of ManageIQ where a low privilege user could enter a crafted Ruby string which would be evaluated. Successful exploitation will allow an attacker to execute arbitrary code with root privileges on the host system. There are patches for this issue in releases named jansa-4, kasparov-2, and lasker-1. If possible, restrict users, via RBAC, to only the part of the application that they need access to. While MiqExpression is widely used throughout the product, restricting users can limit the surface of the attack.

## References
- https://github.com/ManageIQ/manageiq/security/advisories/GHSA-32x4-vj4r-57rq
