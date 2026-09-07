# [H] Cookie Prefix Spoofing in CGI::Cookie.parse

## Summary
Severity: High
Advisory: GHSA-4vf4-qmvg-mh7h
CVE: CVE-2021-41819
CWE: CWE-565
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-4vf4-qmvg-mh7h
Type: github-advisory

## Affected
- RubyGems: `cgi` — affected >=0.3.0 <0.3.1
- RubyGems: `cgi` — affected >=0.2.0 <0.2.1
- RubyGems: `cgi` — affected >=0 <0.1.0.1

## Details
CGI::Cookie.parse in Ruby through 2.6.8 mishandles security prefixes in cookie names. This also affects the CGI gem prior to versions 0.3.1, 0.2.1, 0.1.1, and 0.1.0.1 for Ruby.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41819
- https://hackerone.com/reports/910552
- https://github.com/ruby/cgi
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/cgi/CVE-2021-41819.yml
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IUXQCH6FRKANCVZO2Q7D2SQX33FP3KWN
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTOJGS5IEFDK3UOO7IY4OTTFGHGLSWZF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IUXQCH6FRKANCVZO2Q7D2SQX33FP3KWN
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UTOJGS5IEFDK3UOO7IY4OTTFGHGLSWZF
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20220121-0003
- https://www.ruby-lang.org/en/news/2021/11/24/cookie-prefix-spoofing-in-cgi-cookie-parse-cve-2021-41819
