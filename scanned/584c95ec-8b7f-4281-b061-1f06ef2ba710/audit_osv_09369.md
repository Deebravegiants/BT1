# [H] CVE-2016-9599

## Summary
Severity: High
Advisory: CVE-2016-9599
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2016-9599
Type: osv

## Details
puppet-tripleo before versions 5.5.0, 6.2.0 is vulnerable to an access-control flaw in the IPtables rules management, which allowed the creation of TCP/UDP rules with empty port values. If SSL is enabled, a malicious user could use these open ports to gain access to unauthorized resources.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0025.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9599
