# [M] actionmailer email address processing causes Denial of service

## Summary
Severity: Medium
Advisory: GHSA-rg5m-3fqp-6px8
CVE: CVE-2013-4389
CWE: CWE-134
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-rg5m-3fqp-6px8
Type: github-advisory

## Affected
- RubyGems: `actionmailer` — affected >=3.0.0 <3.2.15

## Details
Multiple format string vulnerabilities in log_subscriber.rb files in the log subscriber component in Action Mailer in Ruby on Rails 3.x before 3.2.15 allow remote attackers to cause a denial of service via a crafted e-mail address that is improperly handled during construction of a log message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4389
- https://github.com/advisories/GHSA-rg5m-3fqp-6px8
- https://github.com/rails/rails/tree/main/actionmailer
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionmailer/CVE-2013-4389.yml
- https://web.archive.org/web/20201208175929/https://groups.google.com/forum/message/raw?msg=ruby-security-ann/yvlR1Vx44c8/elKJkpO2KVgJ
- http://lists.opensuse.org/opensuse-updates/2013-12/msg00091.html
- http://lists.opensuse.org/opensuse-updates/2013-12/msg00094.html
- http://lists.opensuse.org/opensuse-updates/2014-01/msg00003.html
- http://www.debian.org/security/2014/dsa-2887
- http://www.debian.org/security/2014/dsa-2888
