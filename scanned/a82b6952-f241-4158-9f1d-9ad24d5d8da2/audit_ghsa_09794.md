# [M] Agions taskflow-ai vulnerable to os command injection in src/mcp/server/handlers.ts

## Summary
Severity: Medium
Advisory: GHSA-3xp3-pr8x-f755
CVE: CVE-2026-5831
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-3xp3-pr8x-f755
Type: github-advisory

## Affected
- npm: `taskflow-ai` — affected >=0 <2.1.9

## Details
A security flaw has been discovered in Agions taskflow-ai up to 2.1.8. This impacts an unknown function of the file src/mcp/server/handlers.ts of the component terminal_execute. Performing a manipulation results in os command injection. The attack is possible to be carried out remotely. Upgrading to version 2.1.9 will fix this issue. The patch is named c1550b445b9f24f38c4414e9a545f5f79f23a0fe. Upgrading the affected component is recommended. The vendor was contacted early, responded in a very professional manner and quickly released a fixed version of the affected product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5831
- https://github.com/Agions/taskflow-ai/issues/2
- https://github.com/Agions/taskflow-ai/commit/c1550b445b9f24f38c4414e9a545f5f79f23a0fe
- https://github.com/Agions/taskflow-ai
- https://github.com/Agions/taskflow-ai/releases/tag/v2.1.9
- https://vuldb.com/submit/789515
- https://vuldb.com/vuln/356278
- https://vuldb.com/vuln/356278/cti
