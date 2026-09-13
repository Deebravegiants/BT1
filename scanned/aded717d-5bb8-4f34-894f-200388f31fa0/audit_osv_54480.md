# [C] CVE-2023-6879

## Summary
Severity: Critical
Advisory: CVE-2023-6879
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-27
Source: https://osv.dev/vulnerability/CVE-2023-6879
Type: osv

## Details
Increasing the resolution of video frames, while performing a multi-threaded encode, can result in a heap overflow in av1_loop_restoration_dealloc().

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AYONA2XSNFMXLAW4IHLFI5UVV3QRNG5K/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D6C2HN4T2S6GYNTAUXLH45LQZHK7QPHP/
- https://aomedia.googlesource.com/aom/+/refs/tags/v3.7.1
- https://crbug.com/aomedia/3491
