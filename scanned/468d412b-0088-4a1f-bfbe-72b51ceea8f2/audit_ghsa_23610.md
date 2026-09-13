# [M] Path Traversal in scout-browser

## Summary
Severity: Medium
Advisory: GHSA-694v-63fq-fmr4
CVE: CVE-2022-1554
CWE: CWE-22, CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2022-05-04
Source: https://github.com/advisories/GHSA-694v-63fq-fmr4
Type: github-advisory

## Affected
- PyPI: `scout-browser` — affected >=0 <4.52

## Details
Scout is a Variant Call Format (VCF) visualization interface. The Pypi package `scout-browser` is vulnerable to path traversal due to `send_file` call in versions prior to 4.52.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1554
- https://github.com/Clinical-Genomics/scout/issues/3128
- https://github.com/Clinical-Genomics/scout/issues/3302
- https://github.com/Clinical-Genomics/scout/pull/3303
- https://github.com/clinical-genomics/scout/commit/952a2e2319af2d95d22b017a561730feac086ff1
- https://github.com/clinical-genomics/scout
- https://huntr.dev/bounties/7acac778-5ba4-4f02-99e2-e4e17a81e600
