# [M] zlib before 1.3.2 allows CPU consumption via `crc32_combine64` and `crc32_combine_gen64` because...

## Summary
Severity: Medium
Advisory: JLSEC-2026-480
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-480
Type: osv

## Affected
- Julia: `Openresty_jll` — affected >=1.21.4+0 <1.29.203+0
- Julia: `Zlib_jll` — affected >=1.2.12+3 <1.3.2+0
- Julia: `fmusim_jll` — affected >=0 <0.0.39001+0

## Details
zlib before 1.3.2 allows CPU consumption via `crc32_combine64` and `crc32_combine_gen64` because x2nmodp can do right shifts within a loop that has no termination condition.

## References
- https://7asecurity.com/blog/2026/02/zlib-7asecurity-audit
- https://7asecurity.com/blog/2026/02/zlib-7asecurity-audit/
- https://7asecurity.com/reports/pentest-report-zlib-RC1.1.pdf
- https://github.com/advisories/GHSA-h858-mf2m-8jf4
- https://github.com/madler/zlib/issues/904
- https://github.com/madler/zlib/releases/tag/v1.3.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27171
- https://ostif.org/zlib-audit-complete
- https://ostif.org/zlib-audit-complete/
