# [H] CVE-2019-15942

## Summary
Severity: High
Advisory: CVE-2019-15942
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-09-05
Source: https://osv.dev/vulnerability/CVE-2019-15942
Type: osv

## Details
FFmpeg through 4.2 has a "Conditional jump or move depends on uninitialised value" issue in h2645_parse because alloc_rbsp_buffer in libavcodec/h2645_parse.c mishandles rbsp_buffer.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00012.html
- https://security.gentoo.org/glsa/202007-58
- https://trac.ffmpeg.org/ticket/8093
