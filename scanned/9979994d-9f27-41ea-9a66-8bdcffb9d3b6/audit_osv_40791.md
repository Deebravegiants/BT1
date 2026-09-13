# [H] ToolJet Cloud - SSRF to Azure Cloud Infrastructure Compromise

## Summary
Severity: High
Advisory: CVE-2026-55412
Aliases: GHSA-h49f-mhmm-jx4w
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55412
Type: osv

## Details
ToolJet is the open-source foundation am AI-native platform for building and deploying internal tools, workflows and AI agents. Prior to 3.20.178-lts, there's an SSRF in the RestAPI data source component. The RestAPI data source executes HTTP requests server-side, and its private IP filter only checks the hostname string — not the resolved IP. DNS names like 169.254.169.254.nip.io resolve to the Azure IMDS link-local address and bypass the filter entirely. This allows any authenticated user (free tier) to steal Azure managed identity tokens for the AKS production cluster. This vulnerability is fixed in 3.20.178-lts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55412.json
- https://github.com/ToolJet/ToolJet/security/advisories/GHSA-h49f-mhmm-jx4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-55412
