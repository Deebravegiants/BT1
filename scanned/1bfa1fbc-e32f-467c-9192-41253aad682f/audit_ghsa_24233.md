# [C] Puppet Improper Access Control

## Summary
Severity: Critical
Advisory: GHSA-pqj5-7r86-64fv
CVE: CVE-2016-2785
CWE: CWE-284
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pqj5-7r86-64fv
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=4.0.0 <4.4.2

## Details
Puppet Server before 2.3.2 and Ruby puppetmaster in Puppet 4.x before 4.4.2 and in Puppet Agent before 1.4.2 might allow remote attackers to bypass intended auth.conf access restrictions by leveraging incorrect URL decoding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2785
- https://github.com/puppetlabs/puppet/commit/6592a8166572e5f1b7d058474059b8519ec81387
- https://github.com/puppetlabs/puppet
- https://github.com/puppetlabs/puppet/commits/4.4.2
- https://puppet.com/security/cve/cve-2016-2785
- https://security.gentoo.org/glsa/201606-02
