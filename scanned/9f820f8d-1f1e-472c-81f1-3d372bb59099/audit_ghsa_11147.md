# [H] OpenClaw: Gateway HTTP /sessions/:sessionKey/kill Reaches Admin Kill Path Without Caller Scope Binding

## Summary
Severity: High
Advisory: GHSA-9p93-7j67-5pc2
CWE: CWE-226, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-9p93-7j67-5pc2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
## Summary

Gateway HTTP /sessions/:sessionKey/kill Reaches Admin Kill Path Without Caller Scope Binding.

## Details

The HTTP route previously treated any bearer-authenticated request as admin-eligible and could call without binding the action to requester ownership or caller-granted operator scopes. The flaw removes the bearer-token admin fallback and keeps remote session kills on the local-admin or requester-owned path only.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9p93-7j67-5pc2
- https://github.com/openclaw/openclaw/commit/02cf12371f9353a16455da01cc02e6c4ecfc4152
- https://github.com/openclaw/openclaw
