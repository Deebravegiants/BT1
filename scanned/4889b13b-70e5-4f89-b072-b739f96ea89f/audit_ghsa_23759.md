# [M] Puppet Arbitrary Command Execution

## Summary
Severity: Medium
Advisory: GHSA-6xxq-j39w-g3f6
CVE: CVE-2012-1988
CWE: CWE-77, CWE-78
Ecosystem: RubyGems
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6xxq-j39w-g3f6
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=2.6.0 <2.6.15
- RubyGems: `puppet` — affected >=2.7.0 <2.7.13

## Details
Puppet 2.6.x before 2.6.15 and 2.7.x before 2.7.13, and Puppet Enterprise (PE) Users 1.0, 1.1, 1.2.x, 2.0.x, and 2.5.x before 2.5.1 allows remote authenticated users with agent SSL keys and file-creation permissions on the puppet master to execute arbitrary commands by creating a file whose full pathname contains shell metacharacters, then performing a filebucket request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1988
- https://github.com/puppetlabs/puppet/commit/0d6d29933e613fe177e9235415919a5428db67bc
- https://github.com/puppetlabs/puppet/commit/568ded50ec6cc498ad32ff7f086d9f73b5d24c14
- https://web.archive.org/web/20121031092646/http://www.securityfocus.com/bid/52975
- https://web.archive.org/web/20121025194938/http://secunia.com/advisories/48743
- https://web.archive.org/web/20121025194830/http://secunia.com/advisories/49136
- https://web.archive.org/web/20121025113446/http://secunia.com/advisories/48748
- https://web.archive.org/web/20121025112409/http://secunia.com/advisories/48789
- https://web.archive.org/web/20121013181707/http://puppetlabs.com/security/cve/cve-2012-1988
- https://web.archive.org/web/20120816020421/http://projects.puppetlabs.com/projects/1/wiki/Release_Notes#2.6.15
- https://web.archive.org/web/20120513213112/http://projects.puppetlabs.com/issues/13518
- https://web.archive.org/web/20120415105345/http://www.securityfocus.com/bid/52975
- https://hermes.opensuse.org/messages/15087408
- https://hermes.opensuse.org/messages/14523305
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2012-1988.yml
- https://github.com/puppetlabs/puppet
- https://exchange.xforce.ibmcloud.com/vulnerabilities/74796
- http://lists.fedoraproject.org/pipermail/package-announce/2012-April/079227.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-April/079289.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-May/080003.html
