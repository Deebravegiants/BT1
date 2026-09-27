# [C] n8n before 1.123.69 Remote Code Execution via Git Node Configuration Values

## Summary
Severity: Critical
Advisory: CVE-2026-77084
Aliases: GHSA-m87g-qr43-ccvc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77084
Type: osv

## Details
n8n before 1.123.69 (and 2.x before 2.33.4 / 2.34.1) contains a code execution vulnerability in the Git node. The Git node executed certain repository-local git configuration values without neutralizing them, so any subsequent Git node operation against a repository containing a malicious value would execute it as the n8n process user. This is not reachable through the Git node's own configuration controls and requires a separate file-write vulnerability elsewhere to plant the malicious value.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77084.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-m87g-qr43-ccvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-77084
- https://www.vulncheck.com/advisories/n8n-before-remote-code-execution-via-git-node-configuration-values
