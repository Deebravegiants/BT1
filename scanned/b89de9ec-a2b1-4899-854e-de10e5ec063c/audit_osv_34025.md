# [C] Dokploy's Preview Deployments are vulnerable to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-53825
Aliases: GHSA-h67g-mpq5-6ph5
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-07-14
Source: https://osv.dev/vulnerability/CVE-2025-53825
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to version 0.24.3, an unauthenticated preview deployment vulnerability in Dokploy allows any user to execute arbitrary code and access sensitive environment variables by simply opening a pull request on a public repository. This exposes secrets and potentially enables remote code execution, putting all public Dokploy users using these preview deployments at risk. Version 0.24.3 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53825.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-h67g-mpq5-6ph5
- https://nvd.nist.gov/vuln/detail/CVE-2025-53825
- https://github.com/Dokploy/dokploy/commit/1977235d313824b9764f1a06785fb7f73ab7eba2
