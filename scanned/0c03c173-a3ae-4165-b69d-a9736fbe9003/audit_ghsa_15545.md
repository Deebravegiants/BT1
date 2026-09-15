# [H] Remote command execution in promptr

## Summary
Severity: High
Advisory: GHSA-hwxp-6qf7-q3rc
CVE: CVE-2024-46489
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-hwxp-6qf7-q3rc
Type: github-advisory

## Affected
- npm: `@ifnotnowwhen/promptr` — affected >=0

## Details
A remote command execution (RCE) vulnerability in promptr v6.0.7 allows attackers to execute arbitrary commands via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46489
- https://github.com/VulnSphere/LLMVulnSphere/blob/main/Prompt/promptr/RCE_FC_6.0.7.md
- https://github.com/ferrislucas/promptr
