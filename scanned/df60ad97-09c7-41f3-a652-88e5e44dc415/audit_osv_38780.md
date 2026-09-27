# [M] SolidCAM-GPPL-IDE: XML External Entity (XXE) and billion-laughs DoS in VMID parser

## Summary
Severity: Medium
Advisory: CVE-2026-42212
Aliases: GHSA-92vg-f4fq-fxm9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42212
Type: osv

## Details
SolidCAM-GPPL-IDE is an unofficial, independently developed extension, Postprocessor IDE for SolidCAM. From version 1.0.0 to before version 1.0.2, Opening a .gpp file in the SolidCAM Postprocessor IDE extension causes the language server to parse a companion .vmid file from the same directory (naming convention: foo.gpp to foo.vmid). The VMID parser called XDocument.Load(path) without any XmlReaderSettings, inheriting the framework defaults which in .NET 8 allow DTD processing. A malicious .vmid file could therefore: disclose local files via external entity references, exhaust memory via recursive entity expansion, and cause denial of service via oversized or deeply nested XML. This issue has been patched in version 1.0.2.

## References
- https://github.com/anzory/SolidCAM-GPPL-IDE/blob/master/CHANGELOG.md#102--2026-04-20
- https://github.com/anzory/SolidCAM-GPPL-IDE/releases/tag/v1.0.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42212.json
- https://github.com/anzory/SolidCAM-GPPL-IDE/security/advisories/GHSA-92vg-f4fq-fxm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42212
- https://github.com/anzory/SolidCAM-GPPL-IDE/commit/9d0ba808afd143ede448026a5dc681bfdc5c138d
