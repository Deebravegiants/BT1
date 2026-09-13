# [H] JLSEC-2026-1288

## Summary
Severity: High
Advisory: JLSEC-2026-1288
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1288
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
CGI::Cookie.parse in Ruby through 2.6.8 mishandles security prefixes in cookie names. This also affects the CGI gem through 0.3.0 for Ruby.

## References
- https://hackerone.com/reports/910552
- https://hackerone.com/reports/910552
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IUXQCH6FRKANCVZO2Q7D2SQX33FP3KWN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IUXQCH6FRKANCVZO2Q7D2SQX33FP3KWN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTOJGS5IEFDK3UOO7IY4OTTFGHGLSWZF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTOJGS5IEFDK3UOO7IY4OTTFGHGLSWZF/
- https://security.gentoo.org/glsa/202401-27
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20220121-0003/
- https://security.netapp.com/advisory/ntap-20220121-0003/
- https://www.ruby-lang.org/en/news/2021/11/24/cookie-prefix-spoofing-in-cgi-cookie-parse-cve-2021-41819/
- https://www.ruby-lang.org/en/news/2021/11/24/cookie-prefix-spoofing-in-cgi-cookie-parse-cve-2021-41819/
