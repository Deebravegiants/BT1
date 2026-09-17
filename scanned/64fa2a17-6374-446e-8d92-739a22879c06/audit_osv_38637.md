# [H] Flowise: Remote code execution vulnerability in AirtableAgent.ts caused by lack of input verification when using Pandas.

## Summary
Severity: High
Advisory: CVE-2026-41138
Aliases: GHSA-f228-chmx-v6j6
CVSS: 8.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-41138
Type: osv

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. Prior to 3.1.0, there is a remote code execution vulnerability in AirtableAgent.ts caused by lack of input verification when using Pandas. The user’s input is directly applied to the question parameter within the prompt template and it is reflected to the Python code without any sanitization. This vulnerability is fixed in 3.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41138.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-f228-chmx-v6j6
- https://nvd.nist.gov/vuln/detail/CVE-2026-41138
