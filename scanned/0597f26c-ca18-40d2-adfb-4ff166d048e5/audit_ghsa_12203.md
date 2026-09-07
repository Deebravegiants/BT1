# [M] Puppet allows remote attackers to execute arbitrary Ruby programs from the master via the resource_type service

## Summary
Severity: Medium
Advisory: GHSA-cj43-9h3w-v976
CVE: CVE-2013-4761
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-cj43-9h3w-v976
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=2.7.0 <2.7.23
- RubyGems: `puppet` — affected >=3.2.0 <3.2.4

## Details
Unspecified vulnerability in Puppet 2.7.x before 2.7.23 and 3.2.x before 3.2.4, and Puppet Enterprise 2.8.x before 2.8.3 and 3.0.x before 3.0.1, allows remote attackers to execute arbitrary Ruby programs from the master via the resource_type service.  NOTE: this vulnerability can only be exploited utilizing unspecified "local file system access" to the Puppet Master.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4761
- https://github.com/puppetlabs/puppet
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2013-4761.yml
- https://www.puppet.com/security/cve/cve-2013-4761-resourcetype-remote-code-execution-vulnerability
- http://lists.opensuse.org/opensuse-security-announce/2014-01/msg00009.html
- http://puppetlabs.com/security/cve/cve-2013-4761
- http://rhn.redhat.com/errata/RHSA-2013-1283.html
- http://rhn.redhat.com/errata/RHSA-2013-1284.html
- http://www.debian.org/security/2013/dsa-2761
