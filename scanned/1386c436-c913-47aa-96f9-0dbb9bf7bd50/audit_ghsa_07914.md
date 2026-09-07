# [M] OpenClaw: Process Safety - Unvalidated PID Kill via SIGKILL in Process Cleanup

## Summary
Severity: Medium
Advisory: GHSA-jfv4-h8mc-jcp8
CVE: CVE-2026-27486
CWE: CWE-283
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-jfv4-h8mc-jcp8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

OpenClaw CLI process cleanup used system-wide process enumeration and pattern matching to terminate processes without verifying they were owned by the current OpenClaw process. On shared hosts, unrelated processes could be terminated if they matched the pattern.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `< 2026.2.14` (including the latest published version `2026.2.13`)
- Fixed: `2026.2.14` (planned next release)

## Details

The CLI runner cleanup helpers could kill processes matched by command-line patterns without validating process ownership.

## Fix

Process cleanup is now scoped to owned processes only by filtering to direct child PIDs of the current process (`ppid == process.pid`) before sending signals.

Hardening follow-ups:
- Prefer graceful termination for resume cleanup (`SIGTERM`, then `SIGKILL` fallback).
- Reduce false negatives from `ps` argv truncation by preferring wide output (`ps -axww`) with a fallback.
- Tighten command-line token matching to avoid substring matches.

## Fix Commit(s)

- 6084d13b956119e3cf95daaf9a1cae1670ea3557
- eb60e2e1b213740c3c587a7ba4dbf10da620ca66

## Release Process Note

This advisory is pre-set with patched version `2026.2.14`. After `2026.2.14` is published to npm, the remaining step should be to publish this advisory.

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jfv4-h8mc-jcp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-27486
- https://github.com/openclaw/openclaw/commit/6084d13b956119e3cf95daaf9a1cae1670ea3557
- https://github.com/openclaw/openclaw/commit/eb60e2e1b213740c3c587a7ba4dbf10da620ca66
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
