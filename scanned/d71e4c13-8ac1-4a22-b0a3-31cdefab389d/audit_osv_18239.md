# [M] CVE-2020-25467

## Summary
Severity: Medium
Advisory: CVE-2020-25467
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2020-25467
Type: osv

## Details
A null pointer dereference was discovered lzo_decompress_buf in stream.c in Irzip 0.621 which allows an attacker to cause a denial of service (DOS) via a crafted compressed file.

## References
- https://lists.debian.org/debian-lts-announce/2022/04/msg00012.html
- https://bugs.launchpad.net/ubuntu/+source/lrzip/+bug/1893641
- https://github.com/ckolivas/lrzip/issues/163
