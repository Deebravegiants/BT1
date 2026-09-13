# [C] CVE-2024-31581

## Summary
Severity: Critical
Advisory: CVE-2024-31581
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-31581
Type: osv

## Details
FFmpeg version n6.1 was discovered to contain an improper validation of array index vulnerability in libavcodec/cbs_h266_syntax_template.c. This vulnerability allows attackers to cause undefined behavior within the application.

## References
- https://gist.github.com/1047524396/a7e9273e12553775826784035333cdd8
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavcodec/cbs_h266_syntax_template.c#L2048
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31581.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://nvd.nist.gov/vuln/detail/CVE-2024-31581
- https://github.com/ffmpeg/ffmpeg/commit/ce0c178a408d43e71085c28a47d50dc939b60196
