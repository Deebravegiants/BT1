# [C] CVE-2024-22860

## Summary
Severity: Critical
Advisory: CVE-2024-22860
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-27
Source: https://osv.dev/vulnerability/CVE-2024-22860
Type: osv

## Details
Integer overflow vulnerability in FFmpeg before n6.1, allows remote attackers to execute arbitrary code via the jpegxl_anim_read_packet component in the JPEG XL Animation decoder.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=61991
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22860.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22860
- https://github.com/FFmpeg/FFmpeg/commit/d2e8974699a9e35cc1a926bf74a972300d629cd5
