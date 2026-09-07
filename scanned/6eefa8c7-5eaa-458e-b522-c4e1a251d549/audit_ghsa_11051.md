# [M] OpenClaw host-env blocklist missing `GIT_TEMPLATE_DIR` and `AWS_CONFIG_FILE` allows code execution via env override

## Summary
Severity: Medium
Advisory: GHSA-m866-6qv5-p2fg
CVE: CVE-2026-41332
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-m866-6qv5-p2fg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Host execution env sanitization did not block `GIT_TEMPLATE_DIR` or `AWS_CONFIG_FILE`, even though both can redirect trusted tooling to attacker-controlled content.

## Impact

An approved exec request could redirect git or AWS CLI behavior through attacker-controlled configuration and execute untrusted code or load attacker-selected credentials.

## Affected Component

`src/infra/host-env-security-policy.json, src/infra/host-env-security.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `6eb82fba3c` (`Infra: block additional host exec env keys`).

OpenClaw thanks @nicky-cc of Tencent zhuque Lab [https://github.com/Tencent/AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-m866-6qv5-p2fg
- https://github.com/openclaw/openclaw/commit/6eb82fba3cbfd0e50b179c1fada92e1e22dce7fa
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-code-execution-via-missing-environment-variable-blocklist
