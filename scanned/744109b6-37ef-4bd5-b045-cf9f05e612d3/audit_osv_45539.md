# [H] JLSEC-2026-1287

## Summary
Severity: High
Advisory: JLSEC-2026-1287
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1287
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
Date.parse in the date gem through 3.2.0 for Ruby allows ReDoS (regular expression Denial of Service) via a long string. The fixed versions are 3.2.1, 3.1.2, 3.0.2, and 2.0.1.

## References
- https://hackerone.com/reports/1254844
- https://hackerone.com/reports/1254844
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IUXQCH6FRKANCVZO2Q7D2SQX33FP3KWN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IUXQCH6FRKANCVZO2Q7D2SQX33FP3KWN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTOJGS5IEFDK3UOO7IY4OTTFGHGLSWZF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTOJGS5IEFDK3UOO7IY4OTTFGHGLSWZF/
- https://security.gentoo.org/glsa/202401-27
- https://security.gentoo.org/glsa/202401-27
- https://www.ruby-lang.org/en/news/2021/11/15/date-parsing-method-regexp-dos-cve-2021-41817/
- https://www.ruby-lang.org/en/news/2021/11/15/date-parsing-method-regexp-dos-cve-2021-41817/
