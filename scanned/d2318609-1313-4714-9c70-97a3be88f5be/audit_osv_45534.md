# [H] JLSEC-2026-1282

## Summary
Severity: High
Advisory: JLSEC-2026-1282
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1282
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
The REXML gem before 3.2.5 in Ruby before 2.6.7, 2.7.x before 2.7.3, and 3.x before 3.0.1 does not properly address XML round-trip issues. An incorrect document can be produced after parsing and serializing.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WTVFTLFVCSUE5CXHINJEUCKSHU4SWDMT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WTVFTLFVCSUE5CXHINJEUCKSHU4SWDMT/
- https://security.netapp.com/advisory/ntap-20210528-0003/
- https://security.netapp.com/advisory/ntap-20210528-0003/
- https://www.ruby-lang.org/en/news/2021/04/05/xml-round-trip-vulnerability-in-rexml-cve-2021-28965/
- https://www.ruby-lang.org/en/news/2021/04/05/xml-round-trip-vulnerability-in-rexml-cve-2021-28965/
