# [H] CVE-2017-6438

## Summary
Severity: High
Advisory: CVE-2017-6438
CVSS: 7.3 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6438
Type: osv

## Details
Heap-based buffer overflow in the parse_unicode_node function in bplist.c in libimobiledevice libplist 1.12 allows local users to cause a denial of service (out-of-bounds write) and possibly code execution via a crafted plist file.

## References
- http://www.securityfocus.com/bid/97281
- https://github.com/libimobiledevice/libplist/issues/98
