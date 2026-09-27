# [H] CVE-2016-9577

## Summary
Severity: High
Advisory: CVE-2016-9577
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2016-9577
Type: osv

## Details
A vulnerability was discovered in SPICE before 0.13.90 in the server's protocol handling. An authenticated attacker could send crafted messages to the SPICE server causing a heap overflow leading to a crash or possible code execution.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0253.html
- http://rhn.redhat.com/errata/RHSA-2017-0549.html
- http://www.securityfocus.com/bid/96040
- https://access.redhat.com/errata/RHSA-2017:0254
- https://access.redhat.com/errata/RHSA-2017:0552
- https://www.debian.org/security/2017/dsa-3790
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9577
