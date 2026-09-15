# [M] CVE-2017-8846

## Summary
Severity: Medium
Advisory: CVE-2017-8846
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2017-8846
Type: osv

## Details
The read_stream function in stream.c in liblrzip.so in lrzip 0.631 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted archive.

## References
- https://blogs.gentoo.org/ago/2017/05/07/lrzip-use-after-free-in-read_stream-stream-c/
- https://lists.debian.org/debian-lts-announce/2021/08/msg00001.html
- https://security.gentoo.org/glsa/202005-01
- https://github.com/ckolivas/lrzip/issues/71
