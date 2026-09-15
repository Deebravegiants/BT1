# [H] CVE-2024-31582

## Summary
Severity: High
Advisory: CVE-2024-31582
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-31582
Type: osv

## Details
FFmpeg version n6.1 was discovered to contain a heap buffer overflow vulnerability in the draw_block_rectangle function of libavfilter/vf_codecview.c. This vulnerability allows attackers to cause undefined behavior or a Denial of Service (DoS) via crafted input.

## References
- https://gist.github.com/1047524396/b47d5efe3bc420fb91dbb77c73c0fff3
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavfilter/vf_codecview.c#L220
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31582.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://nvd.nist.gov/vuln/detail/CVE-2024-31582
- https://github.com/ffmpeg/ffmpeg/commit/99debe5f823f45a482e1dc08de35879aa9c74bd2
