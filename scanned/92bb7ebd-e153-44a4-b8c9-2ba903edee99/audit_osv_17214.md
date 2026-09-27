# [H] CVE-2020-13790

## Summary
Severity: High
Advisory: CVE-2020-13790
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2020-13790
Type: osv

## Details
libjpeg-turbo 2.0.4, and mozjpeg 4.0.0, has a heap-based buffer over-read in get_rgb_row() in rdppm.c via a malformed PPM input file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00062.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P4D6KNUY7YANSPH7SVQ44PJKSABFKAUB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U6563YHSVZK24MPJXGJVK3CQG7JVWZGK/
- https://usn.ubuntu.com/4386-1/
- https://security.gentoo.org/glsa/202010-03
- https://github.com/libjpeg-turbo/libjpeg-turbo/commit/3de15e0c344d11d4b90f4a47136467053eb2d09a
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/433
