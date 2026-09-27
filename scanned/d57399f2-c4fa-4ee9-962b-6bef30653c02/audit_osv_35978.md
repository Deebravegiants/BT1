# [M] Ffmpeg: ffmpeg: heap buffer overflow in tdsc_load_cursor() via cur_fmt_mono cursor

## Summary
Severity: Medium
Advisory: CVE-2026-18393
CVSS: 5.4 (CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-18393
Type: osv

## Details
A flaw was found in FFmpeg. The tdsc_load_cursor() function writes beyond
the bounds of a heap-allocated buffer when processing crafted TDSC cursor
data. A remote attacker could exploit this by supplying a specially crafted
video file, potentially leading to a denial of service or arbitrary code
execution.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://patchwork.ffmpeg.org/project/ffmpeg/patch/177767065817.63.1948165304485903849@29965ddac10e/
- https://access.redhat.com/security/cve/CVE-2026-18393
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18393.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18393
- https://bugzilla.redhat.com/show_bug.cgi?id=2520309
- https://github.com/FFmpeg/FFmpeg/commit/242ff799c75f20bade946314c8d741d0887ee11c
