# [H] CVE-2018-1097

## Summary
Severity: High
Advisory: CVE-2018-1097
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-1097
Type: osv

## Details
A flaw was found in foreman before 1.16.1. The issue allows users with limited permissions for powering oVirt/RHV hosts on and off to discover the username and password used to connect to the compute resource.

## References
- https://access.redhat.com/errata/RHSA-2018:2927
- https://bugzilla.redhat.com/show_bug.cgi?id=1561723
- https://github.com/theforeman/foreman/pull/5369
- https://projects.theforeman.org/issues/22546
