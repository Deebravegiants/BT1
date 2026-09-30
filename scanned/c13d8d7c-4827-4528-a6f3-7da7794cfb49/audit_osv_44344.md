# [M] Flowintel Note PDF Export Allows Arbitrary Local File Read via Pandoc/XeLaTeX Processing

## Summary
Severity: Medium
Advisory: CVE-2026-81659
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81659
Type: osv

## Details
Affected versions of Flowintel allow attacker-controlled note content to be processed by Pandoc and XeLaTeX during PDF export in a way that can cause local files on the Flowintel server to be read and incorporated into the generated export.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81659.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81659
- https://github.com/flowintel/flowintel/commit/16f618fa36a72c4c5ca3ff0abf7dd67455318ef1
- https://github.com/flowintel/flowintel/commit/2ba9700a5473223639575050bda607f498add7c6
- https://github.com/flowintel/flowintel
