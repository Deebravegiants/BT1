# [C] Buffer overrun in CGI.escape_html

## Summary
Severity: Critical
Advisory: GHSA-5cqm-crxm-6qpv
CVE: CVE-2021-41816
CWE: CWE-190
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-5cqm-crxm-6qpv
Type: github-advisory

## Affected
- RubyGems: `cgi` — affected >=0.3.0 <0.3.1
- RubyGems: `cgi` — affected >=0.2.0 <0.2.1
- RubyGems: `cgi` — affected >=0 <0.1.0.1

## Details
A buffer overrun vulnerability was discovered in CGI.escape_html. This can lead to a buffer overflow when a user passes a very large string (> 700 MB) to CGI.escape_html on a platform where long type takes 4 bytes, typically, Windows.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41816
- https://github.com/ruby/cgi/commit/959ccf0b6a672bcc64aeaa60c6e1f9e728f1e87f
- https://github.com/ruby/cgi/commit/ad079c1cb5f58eba1ffac46da79995fcf94a3a6e
- https://github.com/ruby/cgi/commit/c6a37a671b556eb06140ea89cc465136b24207a6
- https://github.com/ruby/cgi/commit/c728632c1c09d46cfd4ecbff9caaa3651dd1002a
- https://hackerone.com/reports/1328463
- https://www.ruby-lang.org/en/news/2021/11/24/buffer-overrun-in-cgi-escape_html-cve-2021-41816
- https://security.netapp.com/advisory/ntap-20220303-0006
- https://security.gentoo.org/glsa/202401-27
- https://security-tracker.debian.org/tracker/CVE-2021-41816
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UTOJGS5IEFDK3UOO7IY4OTTFGHGLSWZF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IUXQCH6FRKANCVZO2Q7D2SQX33FP3KWN
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTOJGS5IEFDK3UOO7IY4OTTFGHGLSWZF
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IUXQCH6FRKANCVZO2Q7D2SQX33FP3KWN
- https://groups.google.com/g/ruby-security-ann/c/4MQ568ZG47c
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/cgi/CVE-2021-41816.yml
- https://github.com/ruby/cgi
