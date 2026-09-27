# [M] OpenClaw has an unauthorized sender bypass in its stop triggers and /models command authorization

## Summary
Severity: Medium
Advisory: GHSA-8m9v-xpgf-g99m
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-8m9v-xpgf-g99m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
Unauthorized senders could trigger two command paths without sender authorization checks:
1. stop-like natural-language abort triggers
2. `/models` command output

### Impact
An unauthorized sender could disrupt active sessions and view model/auth metadata that should be authorization-gated.

### Fix
Sender authorization is now enforced for stop-like abort triggers and `/models` listings.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8m9v-xpgf-g99m
- https://github.com/openclaw/openclaw
