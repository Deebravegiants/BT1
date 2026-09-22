# [M] CVE-2025-25473

## Summary
Severity: Medium
Advisory: CVE-2025-25473
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-25473
Type: osv

## Details
FFmpeg git master before commit c08d30 was discovered to contain a memory leak in the avformat_free_context function in libavutil/mem.c.

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/blobdiff/4f3c9f2f03378a08692a26532bc3146414717f8c..c08d300481b8ebb846cd43a473988fdbc6793d1b:/libavformat/avformat.c
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/c08d300481b8ebb846cd43a473988fdbc6793d1b
- https://trac.ffmpeg.org/ticket/11419
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25473.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25473
