# [C] CVE-2020-12284

## Summary
Severity: Critical
Advisory: CVE-2020-12284
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-28
Source: https://osv.dev/vulnerability/CVE-2020-12284
Type: osv

## Details
cbs_jpeg_split_fragment in libavcodec/cbs_jpeg.c in FFmpeg 4.1 and 4.2.2 has a heap-based buffer overflow during JPEG_MARKER_SOS handling because of a missing length check.

## References
- https://security.gentoo.org/glsa/202007-58
- https://usn.ubuntu.com/4431-1/
- https://www.debian.org/security/2020/dsa-4722
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=19734
- https://github.com/FFmpeg/FFmpeg/commit/1812352d767ccf5431aa440123e2e260a4db2726
- https://github.com/FFmpeg/FFmpeg/commit/a3a3730b5456ca00587455004d40c047f7b20a99
