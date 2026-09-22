# [H] CVE-2017-13740

## Summary
Severity: High
Advisory: CVE-2017-13740
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13740
Type: osv

## Details
There is a stack-based buffer overflow in Liblouis 3.2.0, triggered in the function parseChars() in compileTranslationTable.c, that will lead to denial of service or possibly unspecified other impact.

## References
- http://www.securityfocus.com/bid/100607
- https://access.redhat.com/errata/RHSA-2017:3111
- https://bugzilla.redhat.com/show_bug.cgi?id=1484306
