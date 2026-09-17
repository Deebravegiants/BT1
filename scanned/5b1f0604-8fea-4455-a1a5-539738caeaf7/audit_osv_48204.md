# [H] CVE-2017-2579

## Summary
Severity: High
Advisory: CVE-2017-2579
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2579
Type: osv

## Details
An out-of-bounds read vulnerability was found in netpbm before 10.61. The expandCodeOntoStack() function has an insufficient code value check, so that a maliciously crafted file could cause the application to crash or possibly allows code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00056.html
- http://www.securityfocus.com/bid/96714
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2579
