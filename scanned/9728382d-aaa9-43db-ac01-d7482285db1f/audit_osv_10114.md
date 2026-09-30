# [H] CVE-2017-13739

## Summary
Severity: High
Advisory: CVE-2017-13739
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13739
Type: osv

## Details
There is a heap-based buffer overflow that causes a more than two thousand bytes out-of-bounds write in Liblouis 3.2.0, triggered in the function resolveSubtable() in compileTranslationTable.c. It will lead to denial of service or remote code execution.

## References
- http://www.securityfocus.com/bid/100607
- https://bugzilla.redhat.com/show_bug.cgi?id=1484299
