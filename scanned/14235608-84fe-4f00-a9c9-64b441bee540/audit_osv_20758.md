# [M] CVE-2021-3671

## Summary
Severity: Medium
Advisory: CVE-2021-3671
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-12
Source: https://osv.dev/vulnerability/CVE-2021-3671
Type: osv

## Details
A null pointer de-reference was found in the way samba kerberos server handled missing sname in TGS-REQ (Ticket Granting Server - Request). An authenticated user could use this flaw to crash the samba server.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00034.html
- https://security.netapp.com/advisory/ntap-20221215-0002/
- https://security.netapp.com/advisory/ntap-20230216-0008/
- https://www.debian.org/security/2022/dsa-5287
- https://bugzilla.redhat.com/show_bug.cgi?id=2013080%2C
- https://bugzilla.samba.org/show_bug.cgi?id=14770%2C
- https://github.com/heimdal/heimdal/commit/04171147948d0a3636bc6374181926f0fb2ec83a
