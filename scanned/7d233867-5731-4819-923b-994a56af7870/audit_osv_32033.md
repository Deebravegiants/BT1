# [M] CVE-2025-22920

## Summary
Severity: Medium
Advisory: CVE-2025-22920
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-22920
Type: osv

## Details
A heap buffer overflow vulnerability in FFmpeg before commit 4bf784c allows attackers to trigger a memory corruption via supplying a crafted media file in avformat when processing tile grid group streams. This can lead to a Denial of Service (DoS).

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/4bf784c0e5615c3f934e677d5de093a8be7da7ae
- https://trac.ffmpeg.org/ticket/11389
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22920.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22920
