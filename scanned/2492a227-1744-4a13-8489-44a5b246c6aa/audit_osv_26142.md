# [H] CVE-2023-51798

## Summary
Severity: High
Advisory: CVE-2023-51798
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2023-51798
Type: osv

## Details
Buffer Overflow vulnerability in Ffmpeg v.N113007-g8d24a28d06 allows a local attacker to execute arbitrary code via a floating point exception (FPE) error at libavfilter/vf_minterpolate.c:1078:60 in interpolate.

## References
- https://ffmpeg.org/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://trac.ffmpeg.org/ticket/10758
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51798.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://nvd.nist.gov/vuln/detail/CVE-2023-51798
