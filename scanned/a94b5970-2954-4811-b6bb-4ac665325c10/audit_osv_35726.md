# [M] CVE-2026-13323

## Summary
Severity: Medium
Advisory: CVE-2026-13323
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-13323
Type: osv

## Details
In Open VSX Registry before 1.0.2, the /vscode/unpkg/ endpoint serves user-supplied HTML files with Content-Type: text/html and without a Content-Security-Policy or Content-Disposition: attachment response header. An unauthenticated attacker can register a publisher account, upload a VSIX containing a crafted HTML payload, and induce an authenticated user to visit the resulting URL. The browser renders the file inline in the open-vsx.org origin context, enabling session token exfiltration, persistent Personal Access Token (PAT) generation, and unauthorized publication of malicious extension versions. Because Open VSX extensions are distributed to VS Code, VSCodium, Cursor, Windsurf, and compatible editors, a compromised extension update constitutes a supply chain attack against all downstream users.

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/485
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13323.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13323
- https://github.com/eclipse-openvsx/openvsx/pull/1922
