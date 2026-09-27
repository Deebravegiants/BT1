# [M] FreeRDP has an out-of-bounds read in ADPCM decoders due to missing predictor/step_index bounds checks

## Summary
Severity: Medium
Advisory: CVE-2026-31885
Aliases: GHSA-h23r-3988-3wf3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-31885
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.24.0, there is an out-of-bounds read in MS-ADPCM and IMA-ADPCM decoders due to unchecked predictor and step_index values from input data. This vulnerability is fixed in 3.24.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31885.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-h23r-3988-3wf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-31885
- https://github.com/FreeRDP/FreeRDP/commit/16df2300e1e3f5a51f68fb1626429e58b531b7c8
