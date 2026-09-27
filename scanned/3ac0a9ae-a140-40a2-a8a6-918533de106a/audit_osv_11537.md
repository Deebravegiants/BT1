# [H] CVE-2017-8361

## Summary
Severity: High
Advisory: CVE-2017-8361
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-30
Source: https://osv.dev/vulnerability/CVE-2017-8361
Type: osv

## Details
The flac_buffer_copy function in flac.c in libsndfile 1.0.28 allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted audio file.

## References
- https://security.gentoo.org/glsa/201811-23
- https://lists.debian.org/debian-lts-announce/2018/12/msg00016.html
- https://blogs.gentoo.org/ago/2017/04/29/libsndfile-global-buffer-overflow-in-flac_buffer_copy-flac-c/
