# [M] CVE-2017-2621

## Summary
Severity: Medium
Advisory: CVE-2017-2621
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2621
Type: osv

## Details
An access-control flaw was found in the OpenStack Orchestration (heat) service before 8.0.0, 6.1.0 and 7.0.2 where a service log directory was improperly made world readable. A malicious system user could exploit this flaw to access sensitive information.

## References
- http://www.securityfocus.com/bid/96280
- https://access.redhat.com/errata/RHSA-2017:1243
- https://access.redhat.com/errata/RHSA-2017:1464
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2621
