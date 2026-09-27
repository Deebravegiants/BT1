# [M] CVE-2017-13743

## Summary
Severity: Medium
Advisory: CVE-2017-13743
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13743
Type: osv

## Details
There is a buffer overflow in Liblouis 3.2.0, triggered in the function _lou_showString() in utils.c, that will lead to a remote denial of service attack.

## References
- http://www.securityfocus.com/bid/100607
- https://access.redhat.com/errata/RHSA-2017:3111
- https://bugzilla.redhat.com/show_bug.cgi?id=1484335
