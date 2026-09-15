# [C] Flowise before 3.1.3 Sandbox Escape to RCE

## Summary
Severity: Critical
Advisory: CVE-2026-73602
Aliases: GHSA-rqh4-rxw3-93rp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73602
Type: osv

## Details
Flowise before 3.1.3 contains a sandbox escape vulnerability in the vm2 JavaScript sandbox that allows authenticated users to execute arbitrary code by exploiting moment locale validation bypass. Attackers can craft a fake String object with a match function that bypasses path traversal checks to load and execute malicious JavaScript files stored in the document store outside the sandbox.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73602.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-rqh4-rxw3-93rp
- https://nvd.nist.gov/vuln/detail/CVE-2026-73602
- https://www.vulncheck.com/advisories/flowise-before-sandbox-escape-to-rce
- https://github.com/FlowiseAI/Flowise/commit/4211bfc8f15746be4019bba557e29a7ba83d54c5
