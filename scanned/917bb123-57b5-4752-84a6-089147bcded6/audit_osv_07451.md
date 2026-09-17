# [M] BIT-ruby-2021-31810

## Summary
Severity: Medium
Advisory: BIT-ruby-2021-31810
Aliases: BIT-ruby-min-2021-31810, CVE-2021-31810
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ruby-2021-31810
Type: osv

## Affected
- Bitnami: `ruby` — affected >=3.0.0 <3.0.2

## Details
An issue was discovered in Ruby through 2.6.7, 2.7.x through 2.7.3, and 3.x through 3.0.1. A malicious FTP server can use the PASV response to trick Net::FTP into connecting back to a given IP address and port. This potentially makes curl extract information about services that are otherwise private and not disclosed (e.g., the attacker can conduct port scans and service banner extractions).

## References
- https://hackerone.com/reports/1145454
- https://lists.debian.org/debian-lts-announce/2021/10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MWXHK5UUHVSHF7HTHMX6JY3WXDVNIHSL/
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20210917-0001/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.ruby-lang.org/en/news/2021/07/07/trusting-pasv-responses-in-net-ftp/
- https://nvd.nist.gov/vuln/detail/CVE-2021-31810
