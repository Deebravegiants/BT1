# [C] Coolify Git Repository Field Command Injection in Project Deployment Workflow

## Summary
Severity: Critical
Advisory: CVE-2025-34161
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-08-27
Source: https://osv.dev/vulnerability/CVE-2025-34161
Type: osv

## Details
Coolify versions prior to v4.0.0-beta.420.7 are vulnerable to a remote code execution vulnerability in the project deployment workflow. The platform allows authenticated users, with low-level member privileges, to inject arbitrary shell commands via the Git Repository field during project creation. By submitting a crafted repository string containing command injection syntax, an attacker can execute arbitrary commands on the underlying host system, resulting in full server compromise.

## References
- https://coolify.io/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34161.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34161
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.420.7
- https://github.com/coollabsio/coolify
- https://github.com/Eyodav/CVE-2025-34161
