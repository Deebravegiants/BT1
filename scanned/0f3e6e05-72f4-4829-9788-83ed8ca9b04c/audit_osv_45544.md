# [M] JLSEC-2026-1291

## Summary
Severity: Medium
Advisory: JLSEC-2026-1291
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1291
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
A ReDoS issue was discovered in the Time component through 0.2.1 in Ruby through 3.2.1. The Time parser mishandles invalid URLs that have specific characters. It causes an increase in execution time for parsing strings to Time objects. The fixed versions are 0.1.1 and 0.2.2.

## References
- https://github.com/ruby/time/releases/
- https://github.com/ruby/time/releases/
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FFZANOQA4RYX7XCB42OO3P24DQKWHEKA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FFZANOQA4RYX7XCB42OO3P24DQKWHEKA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G76GZG3RAGYF4P75YY7J7TGYAU7Z5E2T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G76GZG3RAGYF4P75YY7J7TGYAU7Z5E2T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WMIOPLBAAM3FEQNAXA2L7BDKOGSVUT5Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WMIOPLBAAM3FEQNAXA2L7BDKOGSVUT5Z/
- https://security.gentoo.org/glsa/202401-27
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20230526-0004/
- https://security.netapp.com/advisory/ntap-20230526-0004/
- https://www.ruby-lang.org/en/downloads/releases/
- https://www.ruby-lang.org/en/downloads/releases/
- https://www.ruby-lang.org/en/news/2022/12/25/ruby-3-2-0-released/
- https://www.ruby-lang.org/en/news/2022/12/25/ruby-3-2-0-released/
- https://www.ruby-lang.org/en/news/2023/03/30/redos-in-time-cve-2023-28756/
