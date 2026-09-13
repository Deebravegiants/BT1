# [M] n8n: Instance AI Credential Setup Accepts Unvalidated Probe URL from Fetched Content

## Summary
Severity: Medium
Advisory: CVE-2026-86074
Aliases: GHSA-q5wm-mgqx-fv2f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:L/SI:L/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86074
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 2.37.7 and 2.38.2, the Instance AI credential setup flow accepted a credential test or verification URL without checking that it matched the workflow node's origin. Attacker-controlled fetched content could influence that URL after a user injected it into the setup flow, causing authenticated requests, redirects, or probes to reach another origin. The affected logic includes packages/@n8n/instance-ai/src/tools/workflows/credential-utils.ts and the extractServiceOrigin origin derivation. This issue is fixed in versions 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86074.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-q5wm-mgqx-fv2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-86074
