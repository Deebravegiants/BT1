# [M] CVE-2016-8612

## Summary
Severity: Medium
Advisory: CVE-2016-8612
CVSS: 4.3 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2016-8612
Type: osv

## Details
Apache HTTP Server mod_cluster before version httpd 2.4.23 is vulnerable to an Improper Input Validation in the protocol parsing logic in the load balancer resulting in a Segmentation Fault in the serving httpd process.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://www.securityfocus.com/bid/94939
- https://access.redhat.com/errata/RHSA-2017:0193
- https://access.redhat.com/errata/RHSA-2017:0194
- https://security.netapp.com/advisory/ntap-20180601-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=1387605
