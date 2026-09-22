# [M] facter, hiera, mcollective-client, and puppet affected by untrusted search path vulnerability

## Summary
Severity: Medium
Advisory: GHSA-92v7-pq4h-58j5
CVE: CVE-2014-3248
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-92v7-pq4h-58j5
Type: github-advisory

## Affected
- RubyGems: `facter` — affected >=0 <1.7.6
- RubyGems: `facter` — affected >=2.0.0 <2.0.2
- RubyGems: `hiera` — affected >=0 <1.3.4
- RubyGems: `puppet` — affected >=0 <2.7.26
- RubyGems: `puppet` — affected >=3.0.0 <3.6.2
- RubyGems: `mcollective-client` — affected >=0 <2.5.2

## Details
Untrusted search path vulnerability in Puppet Enterprise 2.8 before 2.8.7, Puppet before 2.7.26 and 3.x before 3.6.2, Facter 1.6.x and 2.x before 2.0.2, Hiera before 1.3.4, and Mcollective before 2.5.2, when running with Ruby 1.9.1 or earlier, allows local users to gain privileges via a Trojan horse file in the current working directory, as demonstrated using (1) `rubygems/defaults/operating_system.rb`, (2) `Win32API.rb`, (3) `Win32API.so`, (4) `safe_yaml.rb`, (5) `safe_yaml/deep.rb`, or (6) `safe_yaml/deep.so`; or (7) `operatingsystem.rb`, (8) `operatingsystem.so`, (9) `osfamily.rb`, or (10) `osfamily.so` in `puppet/confine`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3248
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/facter/CVE-2014-3248.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/hiera/CVE-2014-3248.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mcollective-client/CVE-2014-3248.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2014-3248.yml
- https://web.archive.org/web/20141129061319/http://www.securityfocus.com/bid/68035
- https://web.archive.org/web/20150204183209/http://rowediness.com/2014/06/13/cve-2014-3248-a-little-problem-with-puppet
- https://web.archive.org/web/20150907182402/http://puppetlabs.com/security/cve/cve-2014-3248
