# [M] OpenClaw has ACP CLI approval prompt ANSI escape sequence injection

## Summary
Severity: Medium
Advisory: GHSA-4hmj-39m8-jwc7
CVE: CVE-2026-35651
CWE: CWE-116, CWE-150
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-4hmj-39m8-jwc7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.13 <2026.3.28

## Details
## Summary

ACP CLI approval prompt ANSI escape sequence injection

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `>= 2026.2.13, <= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

ACP tool titles could previously carry ANSI control sequences into approval prompts and permission logs, letting untrusted tool metadata spoof terminal output. Commit `464e2c10a5edceb380d815adb6ff56e1a4c50f60` sanitizes tool titles at the source and broadens ANSI stripping to full CSI sequences.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `464e2c10a5edceb380d815adb6ff56e1a4c50f60`.

## Fix Commit(s)

- `464e2c10a5edceb380d815adb6ff56e1a4c50f60`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4hmj-39m8-jwc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35651
- https://github.com/openclaw/openclaw/commit/464e2c10a5edceb380d815adb6ff56e1a4c50f60
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-ansi-escape-sequence-injection-in-approval-prompt
