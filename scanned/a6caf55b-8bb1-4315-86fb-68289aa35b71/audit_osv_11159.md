# [M] CVE-2017-6435

## Summary
Severity: Medium
Advisory: CVE-2017-6435
CVSS: 5.0 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6435
Type: osv

## Details
The parse_string_node function in bplist.c in libimobiledevice libplist 1.12 allows local users to cause a denial of service (memory corruption) via a crafted plist file.

## References
- http://www.securityfocus.com/bid/97586
- https://lists.debian.org/debian-lts-announce/2020/04/msg00002.html
- https://github.com/libimobiledevice/libplist/commit/fbd8494d5e4e46bf2e90cb6116903e404374fb56
- https://github.com/libimobiledevice/libplist/issues/93
