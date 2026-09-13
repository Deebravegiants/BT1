# [M] CVE-2017-15873

## Summary
Severity: Medium
Advisory: CVE-2017-15873
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-24
Source: https://osv.dev/vulnerability/CVE-2017-15873
Type: osv

## Details
The get_next_block function in archival/libarchive/decompress_bunzip2.c in BusyBox 1.27.2 has an Integer Overflow that may lead to a write access violation.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00037.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00020.html
- https://usn.ubuntu.com/3935-1/
- https://bugs.busybox.net/show_bug.cgi?id=10431
- https://git.busybox.net/busybox/commit/?id=0402cb32df015d9372578e3db27db47b33d5c7b0
