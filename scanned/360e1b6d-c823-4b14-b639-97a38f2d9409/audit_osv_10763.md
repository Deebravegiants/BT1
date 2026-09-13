# [H] CVE-2017-2290

## Summary
Severity: High
Advisory: CVE-2017-2290
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2017-2290
Type: osv

## Details
On Windows installations of the mcollective-puppet-agent plugin, version 1.12.0, a non-administrator user can create an executable that will be executed with administrator privileges on the next "mco puppet" run. Puppet Enterprise users are not affected. This is resolved in mcollective-puppet-agent 1.12.1.

## References
- http://www.securityfocus.com/bid/96583
- https://puppet.com/security/cve/cve-2017-2290
