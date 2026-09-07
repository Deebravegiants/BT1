# [H] Flowise vulnerable to code injection via api/v1

## Summary
Severity: High
Advisory: GHSA-6wp6-22x5-rr3w
CVE: CVE-2024-31621
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2024-04-29
Source: https://github.com/advisories/GHSA-6wp6-22x5-rr3w
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <1.8.1

## Details
An issue in FlowiseAI Inc Flowise prior to v1.8.1 allows a remote attacker to execute arbitrary code via a crafted script to the api/v1 component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31621
- https://github.com/FlowiseAI/Flowise/commit/e32b64344544312bf38b3e1fefe7b26c1776a426
- https://flowiseai.com
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/blob/flowise%401.6.5/packages/server/src/index.ts#L143-L147
- https://www.exploit-db.com/exploits/52001
