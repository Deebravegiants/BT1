# [M] CVE-2024-50613

## Summary
Severity: Medium
Advisory: CVE-2024-50613
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-10-27
Source: https://osv.dev/vulnerability/CVE-2024-50613
Type: osv

## Details
libsndfile through 1.2.2 has a reachable assertion, that may lead to application exit, in mpeg_l3_encode.c mpeg_l3_encoder_close.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50613.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50613
- https://github.com/libsndfile/libsndfile/issues/1034
