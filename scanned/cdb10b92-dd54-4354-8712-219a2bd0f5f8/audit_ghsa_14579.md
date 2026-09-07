# [M] Comrak AST node data is not validated (GHSL-2023-049)

## Summary
Severity: Medium
Advisory: GHSA-5r3x-p7xx-x6q5
CVE: CVE-2023-28631
CWE: CWE-755
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-03-28
Source: https://github.com/advisories/GHSA-5r3x-p7xx-x6q5
Type: github-advisory

## Affected
- crates.io: `comrak` — affected >=0 <0.17.0

## Details
### Impact
A Comrak AST can be constructed manually by a program instead of parsing a Markdown document with `parse_document`. This AST can then be converted to HTML via `html::format_document_with_plugins`. However, the HTML formatting code assumes that the AST is well-formed. For example, many AST notes contain `[u8]` fields which the formatting code assumes is valid UTF-8 data. Several bugs can be triggered if this is not the case.

### Patches

0.17.0 contains adjustments to the AST, storing strings instead of unvalidated byte arrays.

### Workarounds

* Validate UTF-8 correctness of all data when assigning to `&[u8]` and `Vec<u8>` fields in the AST.

### References
n/a

## References
- https://github.com/kivikakk/comrak/security/advisories/GHSA-5r3x-p7xx-x6q5
- https://nvd.nist.gov/vuln/detail/CVE-2023-28631
- https://github.com/kivikakk/comrak/commit/9ff5f8df0ac951f5742d22a72c39b89a15f56639
- https://github.com/kivikakk/comrak
- https://github.com/kivikakk/comrak/releases/tag/0.17.0
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OUYME2VA555X6567H7ORIJQFN4BVGT6N
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PTWZWCT7KCX2KTXTLPUYZ3EHOONG4X46
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VQ3UBC7LE4VPCMZBTADIBL353CH7CPVV
