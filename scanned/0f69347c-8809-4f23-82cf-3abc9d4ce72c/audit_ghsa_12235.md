# [H] Puppet Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-574q-fxfj-wv6h
CVE: CVE-2013-1655
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-574q-fxfj-wv6h
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=2.7.0 <2.7.21
- RubyGems: `puppet` — affected >=3.1.0 <3.1.1

## Details
Puppet 2.7.x before 2.7.21 and 3.1.x before 3.1.1, when running Ruby 1.9.3 or later, allows remote attackers to execute arbitrary code via vectors related to "serialized attributes."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1655
- https://github.com/puppetlabs/puppet
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2013-1655.yml
- https://puppetlabs.com/security/cve/cve-2013-1655
- https://web.archive.org/web/20200228144801/http://www.securityfocus.com/bid/58442
- https://www.puppet.com/security/cve/cve-2013-1655-unauthenticated-remote-code-execution-vulnerability
- http://lists.opensuse.org/opensuse-security-announce/2013-04/msg00004.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00056.html
- http://ubuntu.com/usn/usn-1759-1
- http://www.debian.org/security/2013/dsa-2643
