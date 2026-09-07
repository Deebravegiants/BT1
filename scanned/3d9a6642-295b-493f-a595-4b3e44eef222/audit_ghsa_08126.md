# [H] OpenClaw/Clawdbot Docker Execution has Authenticated Command Injection via PATH Environment Variable

## Summary
Severity: High
Advisory: GHSA-mc68-q9jw-2h3v
CVE: CVE-2026-24763
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-mc68-q9jw-2h3v
Type: github-advisory

## Affected
- npm: `clawdbot` — affected >=0 <2026.1.29

## Details
### Summary
A Command Injection vulnerability existed in Clawdbot’s Docker sandbox execution mechanism due to unsafe handling of the PATH environment variable when constructing shell commands.

An authenticated user able to control environment variables could influence command execution within the container context.
This issue has been fixed and regression tests have been added to prevent reintroduction.

### Impact
In environments where Docker sandbox mode was enabled, authenticated users capable of supplying environment variables could affect the behavior of commands executed inside the container.

This could lead to:
1. Execution of unintended commands inside the container
2. Access to the container filesystem and environment variables
3. Exposure of sensitive data
4. Increased risk in misconfigured or privileged container environments

## References
- https://github.com/clawdbot/clawdbot/security/advisories/GHSA-mc68-q9jw-2h3v
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mc68-q9jw-2h3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-24763
- https://github.com/openclaw/openclaw/commit/771f23d36b95ec2204cc9a0054045f5d8439ea75
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.1.29
