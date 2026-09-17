# [M] CVE-2021-45928

## Summary
Severity: Medium
Advisory: CVE-2021-45928
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45928
Type: osv

## Details
libjxl b02d6b9, as used in libvips 8.11 through 8.11.2 and other products, has an out-of-bounds write in jxl::ModularFrameDecoder::DecodeGroup (called from jxl::FrameDecoder::ProcessACGroup and jxl::ThreadPool::RunCallState<jxl::FrameDecoder::ProcessSections).

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=36456
- https://github.com/libjxl/libjxl/compare/v0.5...v0.6
- https://github.com/libjxl/libjxl/issues/360
- https://github.com/libjxl/libjxl/pull/365
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/libvips/OSV-2021-1055.yaml
