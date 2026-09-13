# [C] datamodel-code-generator Code Injection via Unvalidated customBasePath Schema Field

## Summary
Severity: Critical
Advisory: CVE-2026-63720
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-26
Source: https://osv.dev/vulnerability/CVE-2026-63720
Type: osv

## Details
datamodel-code-generator prior to version 0.70.0 contains a code injection vulnerability that allows attackers who control input schemas to achieve remote code execution by supplying a malicious customBasePath value containing embedded newlines and a dot-free Python expression. The crafted value is emitted verbatim into a generated 'from ... import ...' statement without identifier validation, causing arbitrary Python code to execute when the generated module is imported.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63720.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63720
- https://www.vulncheck.com/advisories/datamodel-code-generator-code-injection-via-unvalidated-custombasepath-schema-field
- https://github.com/koxudaxi/datamodel-code-generator/commit/545a96c5
- https://github.com/koxudaxi/datamodel-code-generator
- https://github.com/rahulreddykarne/CVE-2026-63720-datamodel-code-generator
- https://rahulkarne.com/#/cve/CVE-2026-63720
