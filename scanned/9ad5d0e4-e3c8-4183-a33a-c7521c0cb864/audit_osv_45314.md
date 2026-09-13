# [M] A vulnerability found in libxml2 in versions before 2.9.11 shows that it did not propagate errors...

## Summary
Severity: Medium
Advisory: JLSEC-2025-70
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-70
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.9.12+0

## Details
A vulnerability found in libxml2 in versions before 2.9.11 shows that it did not propagate errors while parsing XML mixed content, causing a NULL dereference. If an untrusted XML document was parsed in recovery mode and post-validated, the flaw could be used to crash the application. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1956522
- https://lists.debian.org/debian-lts-announce/2021/05/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BZOMV5J4PMZAORVT64BKLV6YIZAFDGX6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QVM4UJ3376I6ZVOYMHBNX4GY3NIV52WV/
- https://security.gentoo.org/glsa/202107-05
- https://security.netapp.com/advisory/ntap-20210625-0002/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
