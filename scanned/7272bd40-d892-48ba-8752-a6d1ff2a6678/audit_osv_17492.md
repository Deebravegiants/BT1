# [H] CVE-2020-15503

## Summary
Severity: High
Advisory: CVE-2020-15503
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-02
Source: https://osv.dev/vulnerability/CVE-2020-15503
Type: osv

## Details
LibRaw before 0.20-RC1 lacks a thumbnail size range check. This affects decoders/unpack_thumb.cpp, postprocessing/mem_image.cpp, and utils/thumb_utils.cpp. For example, malloc(sizeof(libraw_processed_image_t)+T.tlength) occurs without validating T.tlength.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7HM2DS6HA4YZREI3BYGS75M6D76WMW62/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CSXAJKZ4VNDYVQULJNY4XDPWHIJDTB4P/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DNGDWTO45TU4KGND75EUUEGUMNSOYC7H/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QCVKD7PTO7UQAVUTBHJAKBKYLPQQGAMZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y34ALB34P3NGQXLF7BG7R6DGRX6XL2JN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZETDVPZQWZWVGIG6JTIEKP5KPVMUE7Y/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00075.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00001.html
- https://github.com/LibRaw/LibRaw/compare/0.20-Beta3...0.20-RC1
- https://lists.debian.org/debian-lts-announce/2022/11/msg00042.html
- https://www.libraw.org/news/libraw-0-20-rc1
- https://github.com/LibRaw/LibRaw/commit/20ad21c0d87ca80217aee47533d91e633ce1864d
