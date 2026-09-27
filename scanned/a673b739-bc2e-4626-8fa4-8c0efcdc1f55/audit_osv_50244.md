# [H] CVE-2020-0034

## Summary
Severity: High
Advisory: CVE-2020-0034
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/CVE-2020-0034
Type: osv

## Details
In vp8_decode_frame of decodeframe.c, there is a possible out of bounds read due to improper input validation. This could lead to remote information disclosure if error correction were turned on, with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-8.0 Android-8.1Android ID: A-62458770

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00048.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00024.html
- https://source.android.com/security/bulletin/2020-03-01
