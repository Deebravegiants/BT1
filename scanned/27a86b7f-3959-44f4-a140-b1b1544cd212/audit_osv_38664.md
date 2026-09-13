# [C] Flowise: Airtable_Agent Code Injection Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-41265
Aliases: GHSA-v38x-c887-992f
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-41265
Type: osv

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. Prior to 3.1.0, the specific flaw exists within the run method of the Airtable_Agents class. The issue results from the lack of proper sandboxing when evaluating an LLM generated python script. Using prompt injection techniques, an unauthenticated attacker with the ability to send prompts to a chatflow using the Airtable Agent node may convince an LLM to respond with a malicious python script that executes attacker controlled commands on the flowise server. This vulnerability is fixed in 3.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41265.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-v38x-c887-992f
- https://nvd.nist.gov/vuln/detail/CVE-2026-41265
