# [M] CVE-2017-9287

## Summary
Severity: Medium
Advisory: CVE-2017-9287
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-29
Source: https://osv.dev/vulnerability/CVE-2017-9287
Type: osv

## Details
servers/slapd/back-mdb/search.c in OpenLDAP through 2.4.44 is prone to a double free vulnerability. A user with access to search the directory can crash slapd by issuing a search including the Paged Results control with a page size of 0.

## References
- http://www.securityfocus.com/bid/98736
- http://www.securitytracker.com/id/1038591
- http://www.debian.org/security/2017/dsa-3868
- https://access.redhat.com/errata/RHSA-2017:1852
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- http://www.openldap.org/its/?findid=8655
- https://bugs.debian.org/863563
- https://www.oracle.com/security-alerts/cpuapr2022.html
