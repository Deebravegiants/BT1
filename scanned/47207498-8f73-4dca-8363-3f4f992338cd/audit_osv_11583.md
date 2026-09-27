# [H] CVE-2017-8844

## Summary
Severity: High
Advisory: CVE-2017-8844
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2017-8844
Type: osv

## Details
The read_1g function in stream.c in liblrzip.so in lrzip 0.631 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted archive.

## References
- https://blogs.gentoo.org/ago/2017/05/07/lrzip-heap-based-buffer-overflow-write-in-read_1g-stream-c/
- https://lists.debian.org/debian-lts-announce/2021/08/msg00001.html
- https://security.gentoo.org/glsa/202005-01
- https://github.com/ckolivas/lrzip/issues/70
