# [M] n8n: Prototype Pollution via Workflow Structure Summary Can Lead to Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-86078
Aliases: GHSA-679f-58pq-4v2c
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86078
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 2.37.7 and 2.38.2, the Instance AI workflow summary used node names and connection keys from stored workflows as ordinary object keys. A workflow submitted through the REST API could contain __proto__ or constructor, causing nested writes to reach Object.prototype in the main n8n process and disrupt later requests. The affected function is summarizeWorkflowStructure in packages/@n8n/instance-ai/src/tools/workflows/summarize-workflow.ts. This issue is fixed in versions 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86078.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-679f-58pq-4v2c
- https://nvd.nist.gov/vuln/detail/CVE-2026-86078
