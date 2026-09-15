# [M] CVE-2025-56226

## Summary
Severity: Medium
Advisory: CVE-2025-56226
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-56226
Type: osv

## Details
Libsndfile <=1.2.2 contains a memory leak vulnerability in the mpeg_l3_encoder_init() function within the mpeg_l3_encode.c file.

## References
- https://gist.github.com/Sisyphus-wang/f9e6e017b7d478bebee6e8187672abc8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56226.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56226
- https://github.com/libsndfile/libsndfile/issues/1089
