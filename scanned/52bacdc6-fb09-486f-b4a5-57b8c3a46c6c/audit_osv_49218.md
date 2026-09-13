# [H] CVE-2018-6508

## Summary
Severity: High
Advisory: CVE-2018-6508
CVSS: 8.0 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-6508
Type: osv

## Details
Puppet Enterprise 2017.3.x prior to 2017.3.3 are vulnerable to a remote execution bug when a specially crafted string was passed into the facter_task or puppet_conf tasks. This vulnerability only affects tasks in the affected modules, if you are not using puppet tasks you are not affected by this vulnerability.

## References
- https://puppet.com/security/cve/CVE-2018-6508
- http://www.securityfocus.com/bid/103020
