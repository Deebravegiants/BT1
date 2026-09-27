# [H] OpenClaw macOS deep link confirmation truncation can conceal executed agent message

## Summary
Severity: High
Advisory: GHSA-7q2j-c4q5-rm27
CVE: CVE-2026-26320
CWE: CWE-451
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-7q2j-c4q5-rm27
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.6-0 <2026.2.14

## Details
### Summary
OpenClaw macOS desktop client registers the `openclaw://` URL scheme. For `openclaw://agent` deep links without an unattended `key`, the app shows a confirmation dialog that previously displayed only the first 240 characters of the message, but executed the full message after the user clicked "Run".

At the time of writing, the OpenClaw macOS desktop client is still in beta.

An attacker could pad the message with whitespace to push a malicious payload outside the visible preview, increasing the chance a user approves a different message than the one that is actually executed.

### Impact
If a user runs the deep link, the agent may perform actions that can lead to arbitrary command execution depending on the user's configured tool approvals/allowlists. This is a social-engineering mediated vulnerability: the confirmation prompt could be made to misrepresent the executed message.

## Affected Versions
- OpenClaw macOS desktop client versions >= 2026.2.6 and <= 2026.2.13.

## Fixed Versions
- 2026.2.14.

### Mitigations
- Do not approve unexpected "Run OpenClaw agent?" prompts triggered while browsing untrusted sites.
- Use unattended deep links only with a valid `key` for trusted personal automations.

### Resolution
Unkeyed deep links now enforce a strict message length limit for confirmation and ignore delivery/routing knobs (`deliver`, `to`, `channel`) unless a valid unattended `key` is provided.

Fix commit: 28d9dd7a772501ccc3f71457b4adfee79084fe6f

---

Fix commit 28d9dd7a772501ccc3f71457b4adfee79084fe6f confirmed on main and in v2026.2.14. Upgrade to `openclaw >= 2026.2.14`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7q2j-c4q5-rm27
- https://nvd.nist.gov/vuln/detail/CVE-2026-26320
- https://github.com/openclaw/openclaw/commit/28d9dd7a772501ccc3f71457b4adfee79084fe6f
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
