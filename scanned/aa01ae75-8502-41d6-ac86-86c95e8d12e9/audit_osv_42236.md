# [H] Plate: SSRF with response disclosure in DOCX image embedding

## Summary
Severity: High
Advisory: CVE-2026-65842
Aliases: GHSA-4q39-2jhr-7qx8
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-65842
Type: osv

## Details
Plate is a rich-text editor with AI and shadcn/ui. Prior to 53.3.2, @platejs/docx-io fetches remote image URLs while converting attacker-controlled HTML through htmlToDocxBlob in a server-side or privileged environment. The converter can make requests to internal network resources and include the fetched image bytes in the generated DOCX, allowing server-side request forgery with response disclosure. Applications can also incur resource consumption from attacker-selected remote responses. This issue is fixed in version 53.3.2.

## References
- https://github.com/udecode/plate/releases/tag/v53.3.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65842.json
- https://github.com/udecode/plate/security/advisories/GHSA-4q39-2jhr-7qx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-65842
- https://github.com/udecode/plate/commit/21aa59926f4bbd421027354823cca09c6700ed73
- https://github.com/udecode/plate/pull/5053
