# [H] CVE-2019-2201

## Summary
Severity: High
Advisory: CVE-2019-2201
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-13
Source: https://osv.dev/vulnerability/CVE-2019-2201
Type: osv

## Details
In generate_jsimd_ycc_rgb_convert_neon of jsimd_arm64_neon.S, there is a possible out of bounds write due to a missing bounds check. This could lead to remote code execution in an unprivileged process with no additional execution privileges needed. User interaction is needed for exploitation.Product: AndroidVersions: Android-8.0 Android-8.1 Android-9 Android-10Android ID: A-120551338

## References
- https://lists.apache.org/thread.html/rc800763a88775ac9abb83b3402bcd0913d41ac65fdfc759af38f2280%40%3Ccommits.mxnet.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2022/05/msg00048.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y4QPASQPZO644STRFTLOD35RIRGWWRNI/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00048.html
- https://security.gentoo.org/glsa/202003-23
- https://source.android.com/security/bulletin/2019-11-01
- https://usn.ubuntu.com/4190-1/
