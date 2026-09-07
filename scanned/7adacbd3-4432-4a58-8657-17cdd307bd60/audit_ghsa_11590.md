# [H] OpenClaw: Unbound interpreter and runtime commands could bypass node-host approval integrity

## Summary
Severity: High
Advisory: GHSA-xf99-j42q-5w5p
CVE: CVE-2026-32979
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-xf99-j42q-5w5p
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, node-host `system.run` approvals could still execute rewritten local code for interpreter and runtime commands when OpenClaw could not bind exactly one concrete local file operand during approval planning.

## Impact
Deployments using node-host `system.run` approval mode could approve a benign local script and then execute different local code if that script changed before execution. This can lead to unintended local code execution as the OpenClaw runtime user.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.8`
- Fixed in: `2026.3.11`

## Technical Details
The approval flow treated some interpreter and runtime forms as approval-backed even when it could not honestly bind a single direct local script file. That left residual approval-integrity gaps for runtime forms outside the directly bound file set.

## Fix
OpenClaw now fails closed for approval-backed interpreter and runtime commands unless it can bind exactly one concrete local file operand, and it extends best-effort direct-file binding for additional runtime forms. The fix shipped in `openclaw@2026.3.11`.

## Workarounds
Upgrade to `2026.3.11` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xf99-j42q-5w5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-32979
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
- https://www.vulncheck.com/advisories/openclaw-unbound-interpreter-and-runtime-commands-bypass-in-node-host-approval
