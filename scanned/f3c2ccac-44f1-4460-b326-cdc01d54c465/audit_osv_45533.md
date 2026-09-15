# [H] JLSEC-2026-1281

## Summary
Severity: High
Advisory: JLSEC-2026-1281
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1281
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
An issue was discovered in Ruby through 2.5.8, 2.6.x through 2.6.6, and 2.7.x through 2.7.1. WEBrick, a simple HTTP server bundled with Ruby, had not checked the transfer-encoding header value rigorously. An attacker may potentially exploit this issue to bypass a reverse proxy (which also has a poor header check), which may lead to an HTTP Request Smuggling attack.

## References
- https://github.com/ruby/webrick/commit/8946bb38b4d87549f0d99ed73c62c41933f97cc7
- https://github.com/ruby/webrick/commit/8946bb38b4d87549f0d99ed73c62c41933f97cc7
- https://hackerone.com/reports/965267
- https://hackerone.com/reports/965267
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PFP3E7KXXT3H3KA6CBZPUOGA5VPFARRJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PFP3E7KXXT3H3KA6CBZPUOGA5VPFARRJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTZURYROG3FFED3TYCQOBV66BS4K6WOV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTZURYROG3FFED3TYCQOBV66BS4K6WOV/
- https://security.gentoo.org/glsa/202401-27
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20210115-0008/
- https://security.netapp.com/advisory/ntap-20210115-0008/
- https://www.ruby-lang.org/en/news/2020/09/29/http-request-smuggling-cve-2020-25613/
- https://www.ruby-lang.org/en/news/2020/09/29/http-request-smuggling-cve-2020-25613/
