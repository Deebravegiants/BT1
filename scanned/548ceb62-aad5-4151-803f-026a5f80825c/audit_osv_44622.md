# [M] n8n before 2.36.2 Credential Exfiltration via Workflow Tool Node

## Summary
Severity: Medium
Advisory: CVE-2026-85166
Aliases: GHSA-4r56-g65c-fm83
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:L)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85166
Type: osv

## Details
n8n before 2.35.4 and 2.36.x before 2.36.2 does not validate credential references in the inline workflow JSON of nodes that execute an inline sub-workflow (e.g., the Workflow Tool node). A shared-workflow editor, or any user creating/updating a workflow via the REST API, Public API, or MCP, can persist a node referencing a credential they do not own. When the workflow is later executed under an identity that holds the credential, the inline sub-workflow resolves the secret and can send it to an attacker-controlled endpoint, resulting in credential exfiltration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85166.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-4r56-g65c-fm83
- https://nvd.nist.gov/vuln/detail/CVE-2026-85166
- https://www.vulncheck.com/advisories/n8n-before-2.36.2-credential-exfiltration-via-workflow-tool-node
