# [H] CVE-2017-8364

## Summary
Severity: High
Advisory: CVE-2017-8364
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-30
Source: https://osv.dev/vulnerability/CVE-2017-8364
Type: osv

## Details
The read_buf function in stream.c in rzip 2.1 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted archive.

## References
- https://lists.debian.org/debian-lts-announce/2020/04/msg00022.html
- https://blogs.gentoo.org/ago/2017/04/29/rzip-heap-based-buffer-overflow-in-read_buf-stream-c/
