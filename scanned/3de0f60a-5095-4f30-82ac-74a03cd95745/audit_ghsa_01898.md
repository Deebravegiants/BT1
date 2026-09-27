# [M] Unsafe HTTP Redirect in Puppet Agent and Puppet Server

## Summary
Severity: Medium
Advisory: GHSA-93j5-g845-9wqp
CVE: CVE-2021-27023
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-02
Source: https://github.com/advisories/GHSA-93j5-g845-9wqp
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=7.0.0 <7.12.1
- RubyGems: `puppet` — affected >=0 <6.25.1

## Details
A flaw was discovered in Puppet Agent and Puppet Server that may result in a leak of HTTP credentials when following HTTP redirects to a different host. This is similar to CVE-2018-1000007

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27023
- https://github.com/puppetlabs/puppet
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2021-27023.yml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/62SELE7EKVKZL4GABFMVYMIIUZ7FPEF7
- https://puppet.com/security/cve/CVE-2021-27023
