# [M] Silent Configuration Failure in Puppet Agent

## Summary
Severity: Medium
Advisory: GHSA-q4g7-jrxv-67r9
CVE: CVE-2021-27025
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-02
Source: https://github.com/advisories/GHSA-q4g7-jrxv-67r9
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=7.0.0 <7.12.1
- RubyGems: `puppet` — affected >=0 <6.25.1

## Details
A flaw was discovered in Puppet Agent where the agent may silently ignore Augeas settings or may be vulnerable to a Denial of Service condition prior to the first 'pluginsync'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27025
- https://github.com/puppetlabs/puppet
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2021-27025.yml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/62SELE7EKVKZL4GABFMVYMIIUZ7FPEF7
- https://puppet.com/security/cve/cve-2021-27025
