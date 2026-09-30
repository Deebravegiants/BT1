# [C] Angular: Multiple Remote Code Execution Vulnerabilities in Angular Language Service VS Code Extension

## Summary
Severity: Critical
Advisory: CVE-2026-49241
Aliases: GHSA-ccq4-xmxr-8hcq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-49241
Type: osv

## Details
The Angular Language Service VS Code Extension provides a rich editing experience for Angular templates. Prior to 21.2.4, the client-side Angular Language Service VS Code extension reads the custom TypeScript SDK paths typescript.tsdk and js/ts.tsdk.path directly from workspace configurations (.vscode/settings.json) without verifying VS Code Workspace Trust state or asking for user consent (located in client/src/client.ts). The client-side extension then passes the parsed settings path as a command-line argument (--tsdk) to the background Node.js language server process. During server initialization, the background language server resolves and dynamically imports (via standard Node.js require()) the module library tsserverlibrary.js relative to the workspace-specified custom directory path. An attacker can exploit this behavior by committing a repository containing a local malicious tsserverlibrary.js script inside a custom folder, and a crafted .vscode/settings.json file pointing to that folder. When a developer opens the repository folder in VS Code, the extension automatically attempts to initialize and load the server, which dynamically resolves, loads, and executes the malicious script silently in the background. This vulnerability is fixed in 21.2.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49241.json
- https://github.com/angular/angular/security/advisories/GHSA-ccq4-xmxr-8hcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-49241
- https://github.com/angular/angular/pull/68857
- https://github.com/angular/angular/pull/68886
