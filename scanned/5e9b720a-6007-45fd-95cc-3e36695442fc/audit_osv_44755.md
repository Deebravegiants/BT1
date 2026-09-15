# [C] n8n: Expression Sandbox Escape in Editor-UI Enables Stored Cross-User JavaScript Execution

## Summary
Severity: Critical
Advisory: CVE-2026-86076
Aliases: GHSA-hw8v-xxg5-vvvx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86076
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 1.123.76, 2.37.7, and 2.38.2, the expression compiler sanitizer resolved through dynamically scoped this and did not reject reserved class member names. A class field named __sanitize could rebind the sanitizer and reach the Function constructor, enabling backend code execution and editor-preview JavaScript execution. The affected AST hook is PrototypeSanitizer in packages/workflow/src/expression-sandboxing.ts. This issue is fixed in versions 1.123.76, 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.76
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86076.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-hw8v-xxg5-vvvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-86076
