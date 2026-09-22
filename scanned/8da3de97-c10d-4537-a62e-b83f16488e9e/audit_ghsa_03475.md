# [M] Improper Certificate Validation in Puppet

## Summary
Severity: Medium
Advisory: GHSA-gqvf-892r-vjm5
CVE: CVE-2020-7942
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-gqvf-892r-vjm5
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=6.0.0 <6.13.0
- RubyGems: `puppet` — affected >=0 <5.5.19

## Details
Previously, Puppet operated on the model that a node with a valid certificate was entitled to all information in the system and that a compromised certificate allowed access to everything in the infrastructure. When a node's catalog falls back to the `default` node, the catalog can be retrieved for a different node by modifying facts for the Puppet run. This issue can be mitigated by setting `strict_hostname_checking = true` in `puppet.conf` on your Puppet master. Puppet 6.13.0 changes the default behavior for strict_hostname_checking from false to true. It is recommended that Puppet Open Source and Puppet Enterprise users that are not upgrading still set strict_hostname_checking to true to ensure secure behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7942
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2020-7942.yml
- https://puppet.com/security/cve/CVE-2020-7942
