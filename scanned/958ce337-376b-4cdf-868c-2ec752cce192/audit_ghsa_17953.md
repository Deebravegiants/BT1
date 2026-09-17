# [M] Apache EventMesh Vulnerable to Server-Side Request Forgery in WebhookUtil.java

## Summary
Severity: Medium
Advisory: GHSA-hf86-8x8v-h7vc
CVE: CVE-2024-39954
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-hf86-8x8v-h7vc
Type: github-advisory

## Affected
- Maven: `org.apache.eventmesh:eventmesh-runtime` — affected >=1.6.0-release

## Details
Server-Side Request Forgery (SSRF) in eventmesh-runtime module in WebhookUtil.java on windows\linux\mac os e.g. allows the attacker can abuse functionality on the server to read or update internal resources.
Users are recommended to upgrade to version 1.12.0 or use the master branch, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39954
- https://github.com/apache/eventmesh
- https://lists.apache.org/thread/v6c96zygqx8xc2k3n2d59mgnm5txhkon
