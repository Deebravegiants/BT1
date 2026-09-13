# [M] actual Allows Electron to Run As Node

## Summary
Severity: Medium
Advisory: GHSA-7rvm-xjpp-63r9
CVE: CVE-2026-42890
CWE: CWE-250, CWE-693, CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-7rvm-xjpp-63r9
Type: github-advisory

## Affected
- npm: `actual` — affected >=0 <26.5.0

## Details
## Summary

A electron run as node vulnerability was identified in `actual` (macOS application, version `25.x (Electron 39.2.7)`).

**Vulnerability Type:** Electron Run As Node

## Description

ELECTRON_RUN_AS_NODE fuse enabled (Electron 39.2.7) — app can be converted to Node.js REPL for arbitrary code execution

## Impact

An attacker who can place a file on disk or control command-line arguments can invoke the signed Actual.app binary with ELECTRON_RUN_AS_NODE=1 to execute arbitrary Node.js code inheriting the apps entitlements and code signature. This bypasses macOS Gatekeeper review of the payload: the Node.js script runs as Actual, under Actuals bundle ID and signed identity, and has access to any entitlements the app carries (network, file access, keychain, automation). Combined with any downloader (browser, mail attachment, Slack link) this becomes a signed-binary-abuse primitive on every Mac with Actual installed.

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-7rvm-xjpp-63r9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42890
- https://actualbudget.org/blog/release-26.5.0
- https://github.com/actualbudget/actual
