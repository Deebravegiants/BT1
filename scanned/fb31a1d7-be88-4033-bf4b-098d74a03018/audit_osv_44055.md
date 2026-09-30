# [M] RansomLook Analysis PDF Generation Allows Server-Side Request Forgery and Arbitrary Local File Access

## Summary
Severity: Medium
Advisory: CVE-2026-78385
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78385
Type: osv

## Details
RansomLook contains insufficient resource validation in the analysis PDF generation functionality. Analysis documents are converted from Markdown to HTML and passed to WeasyPrint for PDF rendering. Prior to the fix, WeasyPrint used its default URL fetcher, allowing resource references contained in an analysis to be resolved without restrictions.

An authenticated attacker able to create or modify an analysis could embed crafted resource references using schemes such as file:// or http://. When the analysis was subsequently rendered as PDF, WeasyPrint would process these references with the privileges and network access of the RansomLook server.

A malicious file:// reference could cause the renderer to access arbitrary files readable by the RansomLook process, potentially exposing sensitive configuration, credentials, or other local data through rendered resources. Network URLs could cause the server to initiate requests to localhost, internal network services, or external systems, resulting in server-side request forgery (SSRF) and potentially bypassing network-level access restrictions.

The patch introduces a dedicated WeasyPrint URL fetcher that permits only data: resources, the RansomLook report logo, and files contained within the analysis asset directory. Network resources and filesystem paths outside these explicitly permitted locations are rejected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78385.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78385
- https://github.com/RansomLook/RansomLook/commit/34dc0285583dae483b4d48c8e98fff942b755f5f
- https://github.com/RansomLook/RansomLook
