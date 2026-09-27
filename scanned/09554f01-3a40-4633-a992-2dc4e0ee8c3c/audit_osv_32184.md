# [M] CVE-2025-25471

## Summary
Severity: Medium
Advisory: CVE-2025-25471
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-25471
Type: osv

## Details
FFmpeg git master before commit fd1772 was discovered to contain a NULL pointer dereference via the component libavformat/mov.c.

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/fd1772b7475d0d5673a5dd314ee78443d0be4cf1
- https://trac.ffmpeg.org/ticket/11417
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25471.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25471
