# [C] OpenClaw: /pair approve command path omitted caller scope subsetting and reopened device pairing escalation

## Summary
Severity: Critical
Advisory: GHSA-hc5h-pmr3-3497
CVE: CVE-2026-33579
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-hc5h-pmr3-3497
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

The `/pair approve` command path called device approval without forwarding caller scopes into the core approval check.

## Impact

A caller that held pairing privileges but not admin privileges could approve a pending device request asking for broader scopes, including admin access.

## Affected Component

`extensions/device-pair/index.ts, src/infra/device-pairing.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `4ee4960de2` (`Pairing: forward caller scopes during approval`).

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hc5h-pmr3-3497
- https://nvd.nist.gov/vuln/detail/CVE-2026-33579
- https://github.com/openclaw/openclaw/commit/4ee4960de2330b5322127f925f3687dc6f105be1
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-missing-caller-scope-validation-in-device-pair-approval
