# [M] Active Record vulnerable to SQL Injection via nested query parameters

## Summary
Severity: Medium
Advisory: GHSA-fh39-v733-mxfr
CVE: CVE-2012-2661
CWE: CWE-89
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-fh39-v733-mxfr
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=3.0.0 <3.0.13
- RubyGems: `activerecord` — affected >=3.1.0 <3.1.5
- RubyGems: `activerecord` — affected >=3.2.0 <3.2.4

## Details
The Active Record component in Ruby on Rails 3.0.x before 3.0.13, 3.1.x before 3.1.5, and 3.2.x before 3.2.4 does not properly implement the passing of request data to a where method in an ActiveRecord class, which allows remote attackers to conduct certain SQL injection attacks via nested query parameters that leverage unintended recursion, a related issue to CVE-2012-2695.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2661
- https://groups.google.com/group/rubyonrails-security/msg/fc2da6c627fc92df?dmode=source&output=gplain
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00016.html
- http://lists.opensuse.org/opensuse-updates/2012-08/msg00046.html
- http://rhn.redhat.com/errata/RHSA-2013-0154.html
