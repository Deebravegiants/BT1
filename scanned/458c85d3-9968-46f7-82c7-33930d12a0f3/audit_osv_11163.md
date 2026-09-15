# [M] CVE-2017-6439

## Summary
Severity: Medium
Advisory: CVE-2017-6439
CVSS: 5.0 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6439
Type: osv

## Details
Heap-based buffer overflow in the parse_string_node function in bplist.c in libimobiledevice libplist 1.12 allows local users to cause a denial of service (out-of-bounds write) via a crafted plist file.

## References
- http://www.securityfocus.com/bid/97278
- https://lists.debian.org/debian-lts-announce/2020/04/msg00002.html
- https://github.com/libimobiledevice/libplist/commit/32ee5213fe64f1e10ec76c1ee861ee6f233120dd
- https://github.com/libimobiledevice/libplist/issues/95
