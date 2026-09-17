# [M] Claude SDK for TypeScript: Memory Tool Path Validation Allows Sandbox Escape to Sibling Directories

## Summary
Severity: Medium
Advisory: GHSA-5474-4w2j-mq4c
CVE: CVE-2026-34451
CWE: CWE-22, CWE-41
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-5474-4w2j-mq4c
Type: github-advisory

## Affected
- npm: `@anthropic-ai/sdk` — affected >=0.79.0 <0.81.0

## Details
The local filesystem memory tool in the Anthropic TypeScript SDK validated model-supplied paths using a string prefix check that did not append a trailing path separator. A model steered by prompt injection could supply a crafted path that resolved to a sibling directory sharing the memory root's name as a prefix, allowing reads and writes outside the sandboxed memory directory.

Users on the affected versions are advised to update to the latest version.

Claude SDK for TypeScript thanks [hackerone.com/nicksim](https://hackerone.com/nicksim) for reporting this issue!

## References
- https://github.com/anthropics/anthropic-sdk-typescript/security/advisories/GHSA-5474-4w2j-mq4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-34451
- https://github.com/anthropics/anthropic-sdk-typescript/commit/0ac69b3438ee9c96b21a7d3c39c07b7cdb6995d9
- https://github.com/anthropics/anthropic-sdk-typescript
- https://github.com/anthropics/anthropic-sdk-typescript/releases/tag/sdk-v0.81.0
