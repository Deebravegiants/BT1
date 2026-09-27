# [M] CVE-2019-13057

## Summary
Severity: Medium
Advisory: CVE-2019-13057
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/CVE-2019-13057
Type: osv

## Details
An issue was discovered in the server in OpenLDAP before 2.4.48. When the server administrator delegates rootDN (database admin) privileges for certain databases but wants to maintain isolation (e.g., for multi-tenant deployments), slapd does not properly stop a rootDN from requesting authorization as an identity from another database during a SASL bind or with a proxyAuthz (RFC 4370) control. (It is not a common configuration to deploy a system where the server administrator and a DB administrator enjoy different levels of trust.)

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00058.html
- http://seclists.org/fulldisclosure/2019/Dec/26
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- https://lists.debian.org/debian-lts-announce/2019/08/msg00024.html
- https://seclists.org/bugtraq/2019/Dec/23
- https://security.netapp.com/advisory/ntap-20190822-0004/
- https://support.apple.com/kb/HT210788
- https://usn.ubuntu.com/4078-1/
- https://usn.ubuntu.com/4078-2/
- https://www.openldap.org/its/?findid=9038
- https://www.openldap.org/lists/openldap-announce/201907/msg00001.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
