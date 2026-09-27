# [M] CVE-2017-8362

## Summary
Severity: Medium
Advisory: CVE-2017-8362
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-30
Source: https://osv.dev/vulnerability/CVE-2017-8362
Type: osv

## Details
The flac_buffer_copy function in flac.c in libsndfile 1.0.28 allows remote attackers to cause a denial of service (invalid read and application crash) via a crafted audio file.

## References
- https://lists.debian.org/debian-lts-announce/2018/12/msg00016.html
- https://security.gentoo.org/glsa/201811-23
- https://blogs.gentoo.org/ago/2017/04/29/libsndfile-invalid-memory-read-in-flac_buffer_copy-flac-c/
