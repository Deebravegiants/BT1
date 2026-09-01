# [?] release(runway): cherry-pick bump: socks to 2.8.8 to resolve ip-address XSS vulnerability (#42485)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-05-07
Source: https://github.com/MetaMask/metamask-extension/commit/e18c18b4d58a50f5775964fb3d2dd01534782b94
Type: security-commit

## Details
release(runway): cherry-pick bump: socks to 2.8.8 to resolve ip-address XSS vulnerability (#42485)

- bump: socks to 2.8.8 to resolve ip-address XSS vulnerability (#42464)

`yarn audit` flagged `ip-address` as release-blocking due to an XSS
vulnerability in its HTML-emitting `Address6` methods. The vulnerable
version was entering the tree transitively via `socks`.

Rather than adding a `resolutions` override, this PR bumps `socks` to
its latest version (`2.8.8`), which already declares
`ip-address@^10.1.1` (the patched range) as its own dependency — making
any resolution entry unnecessary.

- **Lockfile update**
  - Update the `socks` lockfile entry from `2.8.4` → `2.8.8`.
- `socks@2.8.8` natively depends on `ip-address@^10.1.1`, resolving to
`10.2.0`.
- Remove the old `ip-address@9.0.5` entry and its no-longer-needed
`jsbn` subdependency from the lockfile.

- **Impact**
  - Keeps the change scoped to dependency resolution only.
- Addresses the audit finding without a `resolutions` override and
without changing application codepaths.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk lockfile-only dependency bump, but it changes the transitive
networking stack (`socks`/`ip-address`) so unexpected runtime behavior
regressions are the main concern.
> 
> **Overview**
> Updates `yarn.lock` to bump `socks` from `2.8.4` to `2.8.8`, pulling
in `ip-address@^10.1.1` (resolved to `10.2.0`) to address the flagged
vulnerability.

_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/e18c18b4d58a50f5775964fb3d2dd01534782b94_
