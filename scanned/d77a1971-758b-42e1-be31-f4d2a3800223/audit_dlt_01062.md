# [M] nimiq-consensus panics via RequestMacroChain micro-block locator

## Summary
Severity: Medium
Chain: nimiq-consensus
Component: nimiq-consensus
CVE: CVE-2026-34069
CWE: Reachable Assertion
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-48m6-486p-9j8p
Type: github-advisory

## Details
### Impact
 An unauthenticated p2p peer can cause the `RequestMacroChain` message handler task to panic by sending a `RequestMacroChain` message where the first locator hash that is on the victim’s main chain is a micro block hash (not a macro block hash).

In `RequestMacroChain::handle`, the handler selects the locator based only on "is on main chain", then calls `get_macro_blocks()` and panics via `.unwrap()` when the selected hash is not a macro block (`BlockchainError::BlockIsNotMacro`).

### Patches
The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/pull/3660) is formally released as part of [v1.3.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0).

### Workarounds
No known workarounds.
