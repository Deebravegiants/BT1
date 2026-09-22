# [H] CVE-2026-38970

## Summary
Severity: High
Advisory: CVE-2026-38970
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-38970
Type: osv

## Details
pdfcpu through v0.11.1 contains an uncontrolled-recursion denial-of-service issue in pkg/pdfcpu/model/parse.go. The parser descends recursively through nested PDF objects, including arrays, via ParseObjectContext() and parseArray() without enforcing a maximum nesting depth.

## References
- https://github.com/pdfcpu/pdfcpu/blob/a181c19acb322d6b93a1bbda9385a864a9ad6efe/pkg/pdfcpu/model/parse.go#L325-L366
- https://github.com/pdfcpu/pdfcpu/blob/a181c19acb322d6b93a1bbda9385a864a9ad6efe/pkg/pdfcpu/model/parse.go#L942-L970
- https://github.com/pdfcpu/pdfcpu/releases/tag/v0.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38970.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38970
- https://github.com/pdfcpu/pdfcpu/commit/9db810afb52b555ffcae955b32c0be3a73eb53d3
- https://github.com/pdfcpu/pdfcpu
