# [H] There's a flaw in libxml2 in versions before 2.9.11

## Summary
Severity: High
Advisory: JLSEC-2025-71
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-71
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.9.12+0

## Details
There's a flaw in libxml2 in versions before 2.9.11. An attacker who is able to submit a crafted file to be processed by an application linked with libxml2 could trigger a use-after-free. The greatest impact from this flaw is to confidentiality, integrity, and availability.

## References
- http://seclists.org/fulldisclosure/2021/Jul/54
- http://seclists.org/fulldisclosure/2021/Jul/55
- http://seclists.org/fulldisclosure/2021/Jul/58
- http://seclists.org/fulldisclosure/2021/Jul/59
- https://bugzilla.redhat.com/show_bug.cgi?id=1954242
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/05/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BZOMV5J4PMZAORVT64BKLV6YIZAFDGX6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QVM4UJ3376I6ZVOYMHBNX4GY3NIV52WV/
- https://security.gentoo.org/glsa/202107-05
- https://security.netapp.com/advisory/ntap-20210625-0002/
- https://support.apple.com/kb/HT212601
- https://support.apple.com/kb/HT212602
- https://support.apple.com/kb/HT212604
- https://support.apple.com/kb/HT212605
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
