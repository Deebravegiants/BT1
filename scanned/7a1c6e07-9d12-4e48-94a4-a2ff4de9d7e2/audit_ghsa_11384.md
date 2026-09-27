# [M] OpenClaw: MS Teams Feedback Invocation Bypasses Sender Allowlists and Records Unauthorized Session Feedback

## Summary
Severity: Medium
Advisory: GHSA-rf6h-5gpw-qrgq
CVE: CVE-2026-35654
CWE: CWE-288, CWE-863
Ecosystem: npm
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-rf6h-5gpw-qrgq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

MS Teams Feedback Invoke Bypasses Sender Allowlists and Records Unauthorized Session Feedback

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Microsoft Teams feedback invokes previously bypassed sender authorization and could record feedback or trigger reflection for unauthorized senders. Commit `c5415a474bb085404c20f8b312e436997977b1ea` applies the same DM and group authorization checks to feedback invokes.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `c5415a474bb085404c20f8b312e436997977b1ea`.

## Fix Commit(s)

- `c5415a474bb085404c20f8b312e436997977b1ea`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rf6h-5gpw-qrgq
- https://github.com/openclaw/openclaw/commit/c5415a474bb085404c20f8b312e436997977b1ea
- https://github.com/openclaw/openclaw
