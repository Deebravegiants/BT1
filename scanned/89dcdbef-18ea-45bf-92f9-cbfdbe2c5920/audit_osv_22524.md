# [H] CVE-2022-3109

## Summary
Severity: High
Advisory: CVE-2022-3109
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-16
Source: https://osv.dev/vulnerability/CVE-2022-3109
Type: osv

## Details
An issue was discovered in the FFmpeg package, where vp3_decode_frame in libavcodec/vp3.c lacks check of the return value of av_malloc() and will cause a null pointer dereference, impacting availability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3109.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KOMB6WRUC55VWV25IKJTV22KARBUGWGQ/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3109
- https://www.debian.org/security/2023/dsa-5394
- https://bugzilla.redhat.com/show_bug.cgi?id=2153551
- https://github.com/FFmpeg/FFmpeg/commit/656cb0450aeb73b25d7d26980af342b37ac4c568
- https://lists.debian.org/debian-lts-announce/2023/06/msg00016.html
