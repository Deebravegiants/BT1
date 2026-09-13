# [H] Flowise Path Injection at /api/v1/openai-assistants-file

## Summary
Severity: High
Advisory: GHSA-h997-3fxj-p5j8
CVE: CVE-2024-36420
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-h997-3fxj-p5j8
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. In version 1.4.3 of Flowise, the `/api/v1/openai-assistants-file` endpoint in `index.ts` is vulnerable to arbitrary file read due to lack of sanitization of the `fileName` body parameter. No known patches for this issue are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36420
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/blob/e93ce07851cdc0fcde12374f301b8070f2043687/packages/server/src/index.ts#L982
- https://securitylab.github.com/advisories/GHSL-2023-232_GHSL-2023-234_Flowise
