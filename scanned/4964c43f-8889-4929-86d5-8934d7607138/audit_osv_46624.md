# [M] CVE-2014-3250

## Summary
Severity: Medium
Advisory: CVE-2014-3250
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2014-3250
Type: osv

## Details
The default vhost configuration file in Puppet before 3.6.2 does not include the SSLCARevocationCheck directive, which might allow remote attackers to obtain sensitive information via a revoked certificate when a Puppet master runs with Apache 2.4.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1101347
- https://puppet.com/security/cve/CVE-2014-3250
- https://bugzilla.redhat.com/show_bug.cgi?id=1101347
- https://bugzilla.redhat.com/show_bug.cgi?id=1101347
