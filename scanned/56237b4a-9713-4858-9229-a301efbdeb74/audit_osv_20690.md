# [H] CVE-2021-36080

## Summary
Severity: High
Advisory: CVE-2021-36080
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-01
Source: https://osv.dev/vulnerability/CVE-2021-36080
Type: osv

## Details
GNU LibreDWG 0.12.3.4163 through 0.12.3.4191 has a double-free in bit_chain_free (called from dwg_encode_MTEXT and dwg_encode_add_object).

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/libredwg/OSV-2021-495.yaml
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=31724
- https://github.com/LibreDWG/libredwg/commit/9b6e0ff9ef02818df034fc42c3bd149a5ff89342
