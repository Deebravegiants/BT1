# [H] CVE-2023-49502

## Summary
Severity: High
Advisory: CVE-2023-49502
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2023-49502
Type: osv

## Details
Buffer Overflow vulnerability in Ffmpeg v.n6.1-3-g466799d4f5 allows a local attacker to execute arbitrary code via the ff_bwdif_filter_intra_c function in the libavfilter/bwdifdsp.c:125:5 component.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://trac.ffmpeg.org/ticket/10688
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49502.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://nvd.nist.gov/vuln/detail/CVE-2023-49502
- https://github.com/FFmpeg/FFmpeg
