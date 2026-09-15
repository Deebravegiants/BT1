# [M] Ffmpeg: null pointer dereference in firequalizer filter (libavfilter/af_firequalizer.c)

## Summary
Severity: Medium
Advisory: CVE-2025-10256
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2025-10256
Type: osv

## Details
A NULL pointer dereference vulnerability exists in FFmpeg’s Firequalizer filter (libavfilter/af_firequalizer.c) due to a missing check on the return value of av_malloc_array() in the config_input() function. An attacker could exploit this by tricking a victim into processing a crafted media file with the Firequalizer filter enabled, causing the application to dereference a NULL pointer and crash, leading to denial of service.

## References
- https://github.com/FFmpeg/FFmpeg/
- https://access.redhat.com/security/cve/CVE-2025-10256
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10256.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10256
- https://bugzilla.redhat.com/show_bug.cgi?id=2394495
- https://github.com/FFmpeg/FFmpeg/commit/a25462482c02c004d685a8fcf2fa63955aaa0931
- https://github.com/FFmpeg/FFmpeg/commit/d3be186ed1bcdcf2c093d6b13a0e66dc5132be2a
