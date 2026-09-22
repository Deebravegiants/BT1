# [H] OpenClaw has a Command Injection via unescaped environment assignments in Windows Scheduled Task script generation

## Summary
Severity: High
Advisory: GHSA-pj5x-38rw-6fph
CVE: CVE-2026-22176
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-pj5x-38rw-6fph
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
### Summary
A command injection vulnerability existed in Windows Scheduled Task script generation for OpenClaw. Environment values were written into `gateway.cmd` using unquoted `set KEY=VALUE`, which allowed Windows shell metacharacters in config-provided environment variables to break out of assignment context.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.17`
- Patched version: `>= 2026.2.19`
- Latest published vulnerable version at review time (2026-02-19): `2026.2.17`

### Practical Risk Context
For a single-user, localhost-only setup on a personally controlled machine, practical risk is typically low.

This issue becomes materially relevant when configuration or environment values are sourced from less-trusted inputs, for example:
- shared/team config templates,
- copied config snippets,
- setup scripts, automation, or repos that write config,
- any workflow where another party can influence env values before `gateway install`/reinstall.

In those scenarios, it provides a reliable config-to-command-execution path when the scheduled task script is generated and run.

### Details
On Windows, gateway service installation writes a helper batch script and then registers it via Scheduled Task (`schtasks`).
Before the fix, env lines were rendered as `set KEY=VALUE` in `src/daemon/schtasks.ts`, so values containing metacharacters (for example `&`, `|`, `^`, `%`, `!`) could alter command behavior in `cmd.exe`.

The fix now renders quoted assignments (`set "KEY=VALUE"`) with explicit escaping for cmd metacharacters, updates parser compatibility for quoted assignments, and adds regression tests for metacharacter handling and round-trip parsing.

### Fix Commit(s)
- `dafe52e8cf1a041d898cfb304a485fa05e5f58fb`

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-pj5x-38rw-6fph
- https://nvd.nist.gov/vuln/detail/CVE-2026-22176
- https://github.com/openclaw/openclaw/commit/dafe52e8cf1a041d898cfb304a485fa05e5f58fb
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-command-injection-via-unescaped-environment-variables-in-windows-scheduled-task
