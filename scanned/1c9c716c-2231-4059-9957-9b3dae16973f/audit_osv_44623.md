# [C] n8n before 1.123.73 Remote Code Execution via $fromAI Prototype Leak

## Summary
Severity: Critical
Advisory: CVE-2026-85169
Aliases: GHSA-9x83-43r8-5hwc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85169
Type: osv

## Details
n8n versions before 1.123.73, 2.35.4, and 2.36.2 contain an expression sandbox escape in the $fromAI handler. $fromAI resolved a caller-supplied placeholder name without requiring it to be an own property and admitted reserved keys; against a primitive input value it returned a live host-prototype reference. An attacker with workflow-build privilege can walk the prototype chain to the Function constructor and compile/execute arbitrary code in the main n8n process, leading to remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85169.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9x83-43r8-5hwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-85169
- https://www.vulncheck.com/advisories/n8n-before-1.123.73-remote-code-execution-via-fromai-prototype-leak
