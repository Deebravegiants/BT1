# [C] n8n Vulnerable to Remote Code Execution via Expression Injection

## Summary
Severity: Critical
Advisory: GHSA-v98v-ff95-f3cp
CVE: CVE-2025-68613
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-22
Source: https://github.com/advisories/GHSA-v98v-ff95-f3cp
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0.211.0 <1.120.4
- npm: `n8n` — affected >=1.121.0 <1.121.1

## Details
### Impact
n8n contains a critical Remote Code Execution (RCE) vulnerability in its workflow expression evaluation system. Under certain conditions, expressions supplied by authenticated users during workflow configuration may be evaluated in an execution context that is not sufficiently isolated from the underlying runtime.

An authenticated attacker could abuse this behavior to execute arbitrary code with the privileges of the n8n process. Successful exploitation may lead to full compromise of the affected instance, including unauthorized access to sensitive data, modification of workflows, and execution of system-level operations.

### Patches
This issue has been fixed in n8n v1.122.0.

Users are strongly advised to upgrade to version 1.122.0 or later, which introduces additional safeguards to restrict expression evaluation.

### Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:

- Limit workflow creation and editing permissions to fully trusted users only.
- Deploy n8n in a hardened environment with restricted operating system privileges and network access to reduce the impact of potential exploitation.

These workarounds do not fully eliminate the risk and should only be used as short-term measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-v98v-ff95-f3cp
- https://nvd.nist.gov/vuln/detail/CVE-2025-68613
- https://github.com/n8n-io/n8n/commit/08f332015153decdda3c37ad4fcb9f7ba13a7c79
- https://github.com/n8n-io/n8n/commit/1c933358acef527ff61466e53268b41a04be1000
- https://github.com/n8n-io/n8n/commit/39a2d1d60edde89674ca96dcbb3eb076ffff6316
- https://github.com/n8n-io/n8n
- https://www.akamai.com/blog/security-research/2026/feb/zerobot-malware-targets-n8n-automation-platform
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-68613
