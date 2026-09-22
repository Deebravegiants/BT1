# [H] Kubernetes Headlamp Allows Arbitrary Command Injection in macOS Process headlamp@codeSign

## Summary
Severity: High
Advisory: CVE-2025-53542
Aliases: GHSA-34rf-485x-g5h7
CVSS: 7.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-53542
Type: osv

## Details
Headlamp is an extensible Kubernetes web UI. A command injection vulnerability was discovered in the codeSign.js script used in the macOS packaging workflow of the Kubernetes Headlamp project. This issue arises due to the improper use of Node.js's execSync() function with unsanitized input derived from environment variables, which can be influenced by an attacker. The variables ${teamID}, ${entitlementsPath}, and ${config.app} are dynamically derived from the environment or application config and passed directly to the shell command without proper escaping or argument separation. This exposes the system to command injection if any of the values contain malicious input. This vulnerability is fixed in 0.31.1.

## References
- https://advisory.zerodaysec.org/advisory/kubernetes-headlamp-code-signing
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53542.json
- https://github.com/kubernetes-sigs/headlamp/security/advisories/GHSA-34rf-485x-g5h7
- https://nvd.nist.gov/vuln/detail/CVE-2025-53542
- https://github.com/kubernetes-sigs/headlamp/commit/5bc0a9dd87acdf1e04be14619acde687eefa35fb
- https://github.com/kubernetes-sigs/headlamp/pull/3377
