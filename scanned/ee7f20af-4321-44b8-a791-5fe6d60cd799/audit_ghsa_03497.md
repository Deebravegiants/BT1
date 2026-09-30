# [H] Active Record subject to Regular Expression Denial-of-Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-8hc4-xxm3-5ppp
CVE: CVE-2021-22880
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-02
Source: https://github.com/advisories/GHSA-8hc4-xxm3-5ppp
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=5.0.0 <5.2.4.5
- RubyGems: `activerecord` — affected >=6.0.0 <6.0.3.5
- RubyGems: `activerecord` — affected >=6.1.0 <6.1.2.1

## Details
The PostgreSQL adapter in Active Record before 6.1.2.1, 6.0.3.5, 5.2.4.5 suffers from a regular expression denial of service (REDoS) vulnerability. Carefully crafted input can cause the input validation in the `money` type of the PostgreSQL adapter in Active Record to spend too much time in a regular expression, resulting in the potential for a DoS attack. This only impacts Rails applications that are using PostgreSQL along with money type columns that take user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22880
- https://hackerone.com/reports/1023899
- https://discuss.rubyonrails.org/t/cve-2021-22880-possible-dos-vulnerability-in-active-record-postgresql-adapter/77129
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2021-22880.yml
- https://groups.google.com/g/rubyonrails-security/c/ZzUqCh9vyhI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MO5OJ3F4ZL3UXVLJO6ECANRVZBNRS2IH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XQ3NS4IBYE2I3MVMGAHFZBZBIZGHXHT3
- https://security.netapp.com/advisory/ntap-20210805-0009
- https://www.debian.org/security/2021/dsa-4929
