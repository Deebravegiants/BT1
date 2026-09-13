# [M] Flowise: Bcrypt Password Hash Exposure

## Summary
Severity: Medium
Advisory: GHSA-8f47-4rh3-x44m
CVE: CVE-2026-8026
CWE: CWE-200, CWE-312
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-8f47-4rh3-x44m
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
A security flaw has been discovered in FlowiseAI Flowise up to 3.0.12. Affected is the function Login of the file packages/server/src/enterprise/services/account.service.ts of the component API Response Handler. The manipulation results in information disclosure. The attack can be launched remotely. A high complexity level is associated with this attack. The exploitability is told to be difficult. You should upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8026
- https://gist.github.com/YLChen-007/50a553f09aa1c7c04ce18cec13986a91
- https://github.com/FlowiseAI/Flowise
- https://vuldb.com/submit/777656
- https://vuldb.com/vuln/361273
- https://vuldb.com/vuln/361273/cti
