# [H] activerecord vulnerable to SQL Injection

## Summary
Severity: High
Advisory: GHSA-76wq-xw4h-f8wj
CVE: CVE-2012-2695
CWE: CWE-89
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-76wq-xw4h-f8wj
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=3.0.0.beta <3.0.14
- RubyGems: `activerecord` — affected >=3.1.0 <3.1.6
- RubyGems: `activerecord` — affected >=3.2.0 <3.2.6
- RubyGems: `activerecord` — affected >=0 <2.3.15

## Details
The Active Record component in Ruby on Rails efore 2.3.15, 3.0.x before 3.0.14, 3.1.x before 3.1.6, and 3.2.x before 3.2.6 does not properly implement the passing of request data to a where method in an ActiveRecord class, which allows remote attackers to conduct certain SQL injection attacks via nested query parameters that leverage improper handling of nested hashes, a related issue to CVE-2012-2661.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2695
- https://github.com/rails/rails/commit/62f81f4d6b3ee40e9887ffd92ab14714bad93f18
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2012-2695.yml
- https://groups.google.com/g/rubyonrails-security/c/l4L0TEVAz1k/m/Vr84sD9B464J
- https://groups.google.com/group/rubyonrails-security/msg/aee3413fb038bf56?dmode=source&output=gplain
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00016.html
- http://lists.opensuse.org/opensuse-updates/2012-08/msg00046.html
- http://rhn.redhat.com/errata/RHSA-2013-0154.html
