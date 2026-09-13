# [M] Trilium Notes: Stored XSS Leads to Unauthorized Remote Code Execution (RCE) via Unsanitized SVG Attachments

## Summary
Severity: Medium
Advisory: CVE-2026-39311
Aliases: GHSA-p837-cxw3-m964
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-39311
Type: osv

## Details
Trilium Notes is a cross-platform, hierarchical note taking application focused on building large personal knowledge bases. Versions 0.102.1 and prior contain a critical security flaw where lack of SVG sanitization combined with a disabled Content Security Policy (CSP) and a publicly reachable backend execution API results in an unauthenticated Remote Code Execution (RCE). The vulnerability arises from an insecure-by-design architecture: Trilium serves SVG attachments with the image/svg+xml MIME type without any sanitization, and it explicitly disables Helmet's Content Security Policy middleware, removing the primary defense against script execution in served assets. Because the malicious SVG runs under the Same-Origin Policy, it can issue a fetch('/') to extract the csrfToken from the document body. With that token, it can send a signed request to /api/script/exec to execute arbitrary Node.js code on the server. An attacker can compromise the entire server instance simply by tricking an authenticated user into viewing a shared SVG attachment. The issue has been fixed in version 0.102.2.

## References
- https://github.com/TriliumNext/Trilium/releases/tag/v0.102.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39311.json
- https://github.com/TriliumNext/Trilium/security/advisories/GHSA-p837-cxw3-m964
- https://nvd.nist.gov/vuln/detail/CVE-2026-39311
