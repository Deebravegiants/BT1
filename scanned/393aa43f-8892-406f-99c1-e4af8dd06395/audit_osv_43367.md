# [C] Flowise before 3.1.3 Remote Code Execution via Airtable Agent

## Summary
Severity: Critical
Advisory: CVE-2026-73485
Aliases: GHSA-c5hr-rc98-xp3g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73485
Type: osv

## Details
Flowise before 3.1.3 contains a code injection vulnerability in the Airtable Agent node that allows unauthenticated attackers to execute arbitrary Python code by bypassing the pythonCodeValidator blocklist through obfuscation techniques. Attackers can send crafted prompts to a chatflow using the Airtable Agent node to inject malicious Python code that executes in an unsandboxed pyodide environment with full access to the host operating system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73485.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-c5hr-rc98-xp3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-73485
- https://www.vulncheck.com/advisories/flowise-before-remote-code-execution-via-airtable-agent
