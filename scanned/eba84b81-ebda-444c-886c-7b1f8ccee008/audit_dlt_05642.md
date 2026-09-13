# [?] ci: fix undici CVE-2026-22036 in test_report script (#19796)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-11
Source: https://github.com/erigontech/erigon/commit/ad6ca9a2d4dbcccc9b051a441432e1a4d6275755
Type: security-commit

## Details
ci: fix undici CVE-2026-22036 in test_report script (#19796)

## Summary
- Upgrade `@actions/github` v6→v9 and `@actions/core` v1→v2 in
`.github/workflows/scripts/test_report/` to resolve CVE-2026-22036
(undici < 6.23.0, moderate severity)
- Adjust `tsconfig.json` (target ES2022, module/moduleResolution Node16)
and `debug.ts` import for compatibility with newer `@octokit` type
declarations
- `npm audit` now reports 0 vulnerabilities

## Note on pion/dtls/v2
The other Dependabot alert (`github.com/pion/dtls/v2` ≤ 2.2.12) is
blocked on upstream: v2.2.12 is the latest v2 release, and `go-libp2p`
v0.47.0 (latest) still depends on it. No fix is available until upstream
migrates fully to dtls/v3.

## Test plan
- [ ] CI passes (the test_report script runs in GitHub Actions with Node
20+)
- [ ] Verify `npm audit` shows 0 vulnerabilities in
`.github/workflows/scripts/test_report/`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
