# [M] Claude SDK for TypeScript has Insecure Default File Permissions in Local Filesystem Memory Tool

## Summary
Severity: Medium
Advisory: GHSA-p7fg-763f-g4gf
CVE: CVE-2026-41686
CWE: CWE-732
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-p7fg-763f-g4gf
Type: github-advisory

## Affected
- npm: `@anthropic-ai/sdk` — affected >=0.79.0 <0.91.1

## Details
The `BetaLocalFilesystemMemoryTool` in the Anthropic TypeScript SDK created memory files and directories using the Node.js default modes (`0o666` for files, `0o777` for directories), leaving them world-readable on systems with a standard umask and world-writable in environments with a permissive umask such as many Docker base images. A local attacker on a shared host could read persisted agent state, and in containerized deployments could modify memory files to influence subsequent model behavior.

Users on the affected versions are advised to update to the latest version.

Claude SDK  thanks `lucasfutures` for the report.

## References
- https://github.com/anthropics/anthropic-sdk-typescript/security/advisories/GHSA-p7fg-763f-g4gf
- https://nvd.nist.gov/vuln/detail/CVE-2026-41686
- https://github.com/anthropics/anthropic-sdk-typescript
