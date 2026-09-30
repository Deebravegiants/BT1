# [H] OpenClaw: Unsanitized CWD path injection into LLM prompts

## Summary
Severity: High
Advisory: GHSA-2qj5-gwg2-xwc4
CVE: CVE-2026-27001
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-2qj5-gwg2-xwc4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
## Overview
OpenClaw embedded the current working directory (workspace path) into the agent system prompt without sanitization. If an attacker can cause OpenClaw to run inside a directory whose name contains control/format characters (for example newlines or Unicode bidi/zero-width markers), those characters could break the prompt structure and inject attacker-controlled instructions.

## Impact
Prompt injection may alter agent behavior and could lead to unintended tool use or disclosure of sensitive information.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable versions: `< 2026.2.15` (latest published vulnerable version as of 2026-02-16: `2026.2.14`)
- Patched versions: `>= 2026.2.15`

## Fix
The workspace path is now sanitized before it is embedded into any LLM prompt output, stripping Unicode control/format characters and explicit line/paragraph separators. Workspace path resolution also applies the same sanitization as defense-in-depth.

## Fix Commit(s)
- `6254e96acf16e70ceccc8f9b2abecee44d606f79`

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2qj5-gwg2-xwc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-27001
- https://github.com/openclaw/openclaw/commit/6254e96acf16e70ceccc8f9b2abecee44d606f79
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.15
