# [C] Remote code execution and local privilege escalation in Wazuh Windows agent via NetNTLMv2 hash theft

## Summary
Severity: Critical
Advisory: CVE-2024-1243
Aliases: GHSA-3crh-39qv-fxj7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-06-11
Source: https://osv.dev/vulnerability/CVE-2024-1243
Type: osv

## Details
Improper input validation in the Wazuh agent for Windows prior to version 4.8.0 allows an attacker with control over the Wazuh server or agent key to configure the agent to connect to a malicious UNC path. This results in the leakage of the machine account NetNTLMv2 hash, which can be relayed for remote code execution or used to escalate privileges to SYSTEM via AD CS certificate forging and other similar attacks.

## References
- https://pentraze.com/
- https://pentraze.com/vulnerability-reports/CVE-2024-1243/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1243.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-3crh-39qv-fxj7
- https://nvd.nist.gov/vuln/detail/CVE-2024-1243
