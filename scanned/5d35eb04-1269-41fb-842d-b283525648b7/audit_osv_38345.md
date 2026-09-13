# [H] Trilium Notes: Authentication Bypass in Clipper API for Electron (Desktop) Builds

## Summary
Severity: High
Advisory: CVE-2026-39310
Aliases: GHSA-jcvx-vc83-cppw
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-39310
Type: osv

## Details
Trilium Notes is a cross-platform, hierarchical note taking application focused on building large personal knowledge bases. In versions 0.102.1 and prior, the Clipper API in Trilium Desktop (v0.101.3) allows full authentication bypass when running in an Electron environment. When Trilium detects an Electron environment, it explicitly disables authentication middleware for the Clipper API, exposing endpoints such as /api/clipper/notes to the network with no password, API token, or CSRF protection. An attacker on a shared network (for example, a corporate LAN or public Wi-Fi) can scan for open high-range ports using a tool like nmap, since Trilium often binds to ports such as 37840. Once a candidate port is found, an unauthenticated request to the Clipper handshake endpoint, which also bypasses authentication, confirms a Trilium instance by returning the application name and protocol version. This facilitates unauthorized data access, phishing, and local system compromise. The issue has been fixed in version 0.102.2.

## References
- https://github.com/TriliumNext/Trilium/releases/tag/v0.102.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39310.json
- https://github.com/TriliumNext/Trilium/security/advisories/GHSA-jcvx-vc83-cppw
- https://nvd.nist.gov/vuln/detail/CVE-2026-39310
