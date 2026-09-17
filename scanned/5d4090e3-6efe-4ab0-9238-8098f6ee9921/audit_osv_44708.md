# [M] ConvertX 0.17.0 Arbitrary File Read via LaTeX Input Directives

## Summary
Severity: Medium
Advisory: CVE-2026-85618
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85618
Type: osv

## Details
ConvertX 0.17.0 contains an arbitrary file read vulnerability in the xelatex converter that allows authenticated users to read files by uploading LaTeX files with input directives. Attackers can upload .tex files containing \\input{path} or \\verbatiminput{path} directives to have the TeX engine read arbitrary files accessible to the server process and include them in downloadable PDF output.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85618.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85618
- https://www.vulncheck.com/advisories/convertx-0.17.0-arbitrary-file-read-via-latex-input-directives
- https://github.com/C4illin/ConvertX/issues/573
- https://github.com/C4illin/ConvertX
- https://github.com/C4illin/ConvertX/blob/v0.18.0/src/converters/xelatex.ts
