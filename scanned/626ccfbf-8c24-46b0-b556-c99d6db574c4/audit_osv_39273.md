# [M] Exposed tokens in SUSE Rancher AI Agent logs

## Summary
Severity: Medium
Advisory: CVE-2026-44934
Aliases: GHSA-5r2r-h824-fr5v
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-44934
Type: osv

## Details
A information disclosure when DEBUG loglevel is set in SUSE Rancher AI Agent 1.0 before 1.0.2 could leak API keys or LLM response text with potential sensitive data into logfiles, allowing local attackers to misuse respective gained data or credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44934.json
- https://github.com/rancher/rancher-ai-agent/security/advisories/GHSA-5r2r-h824-fr5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44934
- https://github.com/rancher/rancher-ai-agent
