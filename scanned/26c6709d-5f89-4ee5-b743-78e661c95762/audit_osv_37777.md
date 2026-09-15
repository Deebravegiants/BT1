# [H] AutoGPT: Denial of Service (DoS) via Resource Exhaustion in text templating features

## Summary
Severity: High
Advisory: CVE-2026-33235
Aliases: GHSA-ppw9-h7rv-gwq9
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-33235
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. In versions prior to 0.6.52, the Fill Text Template block is vulnerable to a Denial of Service (DoS) attack. While the backend implements a SandboxedEnvironment to prevent unauthorized attribute access (e.g., blocking __class__), it fails to limit the computational complexity or execution time of the expressions. An attacker can input computationally expensive Python/Jinja2 expressions that consume the server's CPU and memory, leading to a complete system hang or crash. In multi-tenant or self-hosted environments, this results in a complete service outage and "noisy neighbor" effects that require manual administrative intervention to recover. This issue has been fixed in version 0.6.52.

## References
- https://github.com/Significant-Gravitas/AutoGPT/releases/tag/autogpt-platform-beta-v0.6.52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33235.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-ppw9-h7rv-gwq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33235
