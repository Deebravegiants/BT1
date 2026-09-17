# [C] Angular: Remote Code Execution via JSDoc Hover Command Injection in VS Code Angular Language Service Extension

## Summary
Severity: Critical
Advisory: CVE-2026-50178
Aliases: GHSA-q94j-3wj3-4xcm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-50178
Type: osv

## Details
The Angular Language Service VS Code Extension provides a rich editing experience for Angular templates. the client-side Angular Language Service VS Code extension configures the tooltip Markdown renderer with the isTrusted: true option (located in client/src/client.ts). This setting instructs VS Code to trust all rendered content it receives, which enables active elements such as command: URIs. However, the background Angular Language Server process fails to escape or sanitize brackets, raw links, and control characters from JSDoc strings before forwarding the hover Markdown content (located in server/src/handlers/hover.ts and server/src/text_render.ts). An attacker can leverage this behavior by crafting a project TypeScript or JavaScript file (or a third-party npm package dependency) containing a malicious JSDoc tooltip with an embedded active command link. When a developer hovers over the target symbol to render the tooltip and clicks the malicious link, the IDE executes the command sequence directly on the developer's host machine. Prior to 21.2.4,  This vulnerability is fixed in 21.2.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50178.json
- https://github.com/angular/angular/security/advisories/GHSA-q94j-3wj3-4xcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-50178
