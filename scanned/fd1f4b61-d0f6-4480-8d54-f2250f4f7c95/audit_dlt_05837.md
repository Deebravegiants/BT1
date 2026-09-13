# [?] fix: crash when trace-logging in tests (#5529)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2025-07-02
Source: https://github.com/XRPLF/rippled/commit/c2f3e2e2637d68183458899b786588ee2b73602d
Type: security-commit

## Details
fix: crash when trace-logging in tests (#5529)

This PR fixes a crash in tests when the test `Env is run at trace/debug log level.

This issue only affects tests, and only if logging at trace/debug level, so really only relevant during rippled development, and does not affect production servers.
