# [H] CVE-2019-13565

## Summary
Severity: High
Advisory: CVE-2019-13565
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/CVE-2019-13565
Type: osv

## Details
An issue was discovered in OpenLDAP 2.x before 2.4.48. When using SASL authentication and session encryption, and relying on the SASL security layers in slapd access controls, it is possible to obtain access that would otherwise be denied via a simple bind for any identity covered in those ACLs. After the first SASL bind is completed, the sasl_ssf value is retained for all new non-SASL connections. Depending on the ACL configuration, this can affect different types of operations (searches, modifications, etc.). In other words, a successful authorization step completed by one user affects the authorization requirement for a different user.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://support.f5.com/csp/article/K98008862?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00058.html
- http://seclists.org/fulldisclosure/2019/Dec/26
- https://lists.debian.org/debian-lts-announce/2019/08/msg00024.html
- https://seclists.org/bugtraq/2019/Dec/23
- https://support.apple.com/kb/HT210788
- https://usn.ubuntu.com/4078-1/
- https://usn.ubuntu.com/4078-2/
- https://www.openldap.org/its/index.cgi/?findid=9052
- https://www.openldap.org/lists/openldap-announce/201907/msg00001.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
