# [H] CVE-2017-2672

## Summary
Severity: High
Advisory: CVE-2017-2672
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-21
Source: https://osv.dev/vulnerability/CVE-2017-2672
Type: osv

## Details
A flaw was found in foreman before version 1.15 in the logging of adding and registering images. An attacker with access to the foreman log file would be able to view passwords for provisioned systems in the log file, allowing them to access those systems.

## References
- http://www.securityfocus.com/bid/97526
- https://access.redhat.com/errata/RHSA-2018:0336
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2672
- https://projects.theforeman.org/issues/19169
