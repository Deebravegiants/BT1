# [M] CVE-2020-0499

## Summary
Severity: Medium
Advisory: CVE-2020-0499
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-0499
Type: osv

## Details
In FLAC__bitreader_read_rice_signed_block of bitreader.c, there is a possible out of bounds read due to a heap buffer overflow. This could lead to remote information disclosure with no additional execution privileges needed. User interaction is needed for exploitation.Product: AndroidVersions: Android-11Android ID: A-156076070

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/33W6XZAAEJYRGU3XYHRO7XSYEA7YACUB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KNZYTAU5UWBVXVJ4VHDWPR66ZVDLQZRE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VPA5GAEKPXKAHGHHBI4X7AFNI4BMOVG3/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00001.html
- https://source.android.com/security/bulletin/pixel/2020-12-01
