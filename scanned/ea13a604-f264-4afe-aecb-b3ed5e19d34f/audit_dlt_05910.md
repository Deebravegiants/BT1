# [?] release(runway): cherry-pick fix: handle scientific notation in parseBalanceWithDecimals to prevent BigInt crash cp-13.34.1 (#43334)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-06-08
Source: https://github.com/MetaMask/metamask-extension/commit/612589bd33eb7476f345d2849f3157c8afdd4a79
Type: security-commit

## Details
release(runway): cherry-pick fix: handle scientific notation in parseBalanceWithDecimals to prevent BigInt crash cp-13.34.1 (#43334)

- fix: handle scientific notation in parseBalanceWithDecimals to prevent
BigInt crash cp-13.34.1 (#43314)

When BackendWebsocketDataSource stores a very small balance (e.g. 1 wei
with 18 decimals), BigNumber.js .toFixed() returns scientific notation
like "1e-18". The existing parseBalanceWithDecimals splits on "." which
fails for scientific notation, producing strings like
"1e-18000000000000000000" that crash BigInt() with SyntaxError.

Adds parseScientificNotationBalance to correctly convert scientific
notation strings to base-unit bigints before the normal fixed-point
path.

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

<!--
Write a short description of the changes included in this pull request,
also include relevant motivation and context. Have in mind the following
questions:
1. What is the reason for the change?
2. What is the improvement/solution?
-->

## **Changelog**

<!--
If this PR is not End-User-Facing and should not show up in the
CHANGELOG, you can choose to either:
1. Write `CHANGELOG entry: null`
2. Label with `no-changelog`

_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/612589bd33eb7476f345d2849f3157c8afdd4a79_
