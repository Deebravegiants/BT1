# [M] Ffmpeg: null pointer dereference in ffmpeg als decoder (libavcodec/alsdec.c)

## Summary
Severity: Medium
Advisory: CVE-2025-7700
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-7700
Type: osv

## Details
A flaw was found in FFmpeg’s ALS audio decoder, where it does not properly check for memory allocation failures. This can cause the application to crash when processing certain malformed audio files. While it does not lead to data theft or system control, it can be used to disrupt services and cause a denial of service.

## References
- https://github.com/FFmpeg/FFmpeg/
- https://access.redhat.com/security/cve/CVE-2025-7700
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7700.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7700
- https://bugzilla.redhat.com/show_bug.cgi?id=2380420
- https://github.com/FFmpeg/FFmpeg/commit/35a6de137a39f274d5e01ed0e0e6c4f04d0aaf07
