# [H] JLSEC-2026-1285

## Summary
Severity: High
Advisory: JLSEC-2026-1285
Ecosystem: Julia
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1285
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
An issue was discovered in Ruby through 2.6.7, 2.7.x through 2.7.3, and 3.x through 3.0.1. Net::IMAP does not raise an exception when StartTLS fails with an an unknown response, which might allow man-in-the-middle attackers to bypass the TLS protections by leveraging a network position between the client and the registry to block the StartTLS command, aka a "StartTLS stripping attack."

## References
- https://github.com/ruby/ruby/commit/a21a3b7d23704a01d34bd79d09dc37897e00922a
- https://github.com/ruby/ruby/commit/a21a3b7d23704a01d34bd79d09dc37897e00922a
- https://hackerone.com/reports/1178562
- https://hackerone.com/reports/1178562
- https://lists.debian.org/debian-lts-announce/2021/10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://security.gentoo.org/glsa/202401-27
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20210902-0004/
- https://security.netapp.com/advisory/ntap-20210902-0004/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.ruby-lang.org/en/news/2021/07/07/starttls-stripping-in-net-imap/
- https://www.ruby-lang.org/en/news/2021/07/07/starttls-stripping-in-net-imap/
