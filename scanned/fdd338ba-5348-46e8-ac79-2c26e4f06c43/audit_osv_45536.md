# [M] JLSEC-2026-1284

## Summary
Severity: Medium
Advisory: JLSEC-2026-1284
Ecosystem: Julia
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1284
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
An issue was discovered in Ruby through 2.6.7, 2.7.x through 2.7.3, and 3.x through 3.0.1. A malicious FTP server can use the PASV response to trick Net::FTP into connecting back to a given IP address and port. This potentially makes curl extract information about services that are otherwise private and not disclosed (e.g., the attacker can conduct port scans and service banner extractions).

## References
- https://hackerone.com/reports/1145454
- https://hackerone.com/reports/1145454
- https://lists.debian.org/debian-lts-announce/2021/10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MWXHK5UUHVSHF7HTHMX6JY3WXDVNIHSL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MWXHK5UUHVSHF7HTHMX6JY3WXDVNIHSL/
- https://security.gentoo.org/glsa/202401-27
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20210917-0001/
- https://security.netapp.com/advisory/ntap-20210917-0001/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.ruby-lang.org/en/news/2021/07/07/trusting-pasv-responses-in-net-ftp/
- https://www.ruby-lang.org/en/news/2021/07/07/trusting-pasv-responses-in-net-ftp/
