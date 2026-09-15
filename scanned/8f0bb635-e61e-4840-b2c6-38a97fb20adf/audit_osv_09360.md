# [H] CVE-2016-9583

## Summary
Severity: High
Advisory: CVE-2016-9583
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-9583
Type: osv

## Details
An out-of-bounds heap read vulnerability was found in the jpc_pi_nextpcrl() function of jasper before 2.0.6 when processing crafted input.

## References
- http://www.securityfocus.com/bid/94925
- https://access.redhat.com/errata/RHSA-2017:1208
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9583
- https://github.com/mdadams/jasper/commit/aa0b0f79ade5eef8b0e7a214c03f5af54b36ba7d
- https://github.com/mdadams/jasper/commit/f25486c3d4aa472fec79150f2c41ed4333395d3d
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
