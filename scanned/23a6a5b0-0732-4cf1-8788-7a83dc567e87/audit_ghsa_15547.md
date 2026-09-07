# [M] Flowise and Flowise Chat Embed vulnerable to Stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-m5p9-xvxj-64c8
CVE: CVE-2024-9148
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-m5p9-xvxj-64c8
Type: github-advisory

## Affected
- npm: `flowise-embed` — affected >=0 <2.0.0
- npm: `flowise` — affected >=0 <2.1.1

## Details
Flowise < 2.1.1 suffers from a Stored Cross-Site vulnerability due to a lack of input sanitization in Flowise Chat Embed < 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9148
- https://github.com/FlowiseAI/Flowise/commit/8375ebb4ec1ebb2b1295561cc0f63486a29f3fde
- https://github.com/FlowiseAI/FlowiseChatEmbed/commit/6a9645df41371cb69f251038d501ec87b1304c84
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%402.1.1
- https://github.com/FlowiseAI/FlowiseChatEmbed
- https://github.com/FlowiseAI/FlowiseChatEmbed/releases/tag/flowise-embed%402.0.0
- https://www.tenable.com/security/research/tra-2024-40
