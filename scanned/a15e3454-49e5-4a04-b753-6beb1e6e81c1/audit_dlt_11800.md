# [?] fix: crashing app on mobile on a successful tx (#6890)

## Summary
Severity: Unknown
Chain: Tooling
Component: MetaMask/core
Published: 2025-10-17
Source: https://github.com/MetaMask/core/commit/58f93e2a9b130efd263c63bedbf5da62b841c91e
Type: security-commit

## Details
fix: crashing app on mobile on a successful tx (#6890)

## Explanation

<!--
Thanks for your contribution! Take a moment to answer these questions so
that reviewers have the information they need to properly understand
your changes:

* What is the current state of things and why does it need to change?
* What is the solution your changes offer and how does it work?
* Are there any changes whose purpose might not obvious to those
unfamiliar with the domain?
* If your primary goal was to update one package but you found you had
to update another one along the way, why did you do so?
* If you had to upgrade a dependency, why did you do so?
-->

This PR fixes an issue in Mobile where the app would crash after a
successful tx.

## References

<!--
Are there any issues that this pull request is tied to?
Are there other links that reviewers should consult to understand these
changes better?
Are there client or consumer pull requests to adopt any breaking
changes?

For example:

* Fixes #12345
* Related to #67890
-->

Related to https://github.com/MetaMask/metamask-mobile/pull/21374

## Checklist

- [x] I've updated the test suite for new or updated code as appropriate
- [x] I've updated documentation (JSDoc, Markdown, etc.) for new or
updated code as appropriate
- [x] I've communicated my changes to consumers by [updating changelogs
for packages I've
changed](https://github.com/MetaMask/core/tree/main/docs/contributing.md#updating-changelogs),
highlighting breaking changes as necessary
- [ ] I've prepared draft pull requests for clients and consumer
packages to resolve any breaking changes

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Safely handle missing `topics[0]` when parsing ERC-20 transfer logs to
avoid Mobile crash after successful transactions; update changelog.
> 
> - **Fixes**:
> - Safely parse ERC-20 transfer logs in
`packages/bridge-status-controller/src/utils/swap-received-amount.ts` by
using optional access for `topics[0]` to prevent crashes when undefined
on Mobile post-transaction.
> - **Docs**:
> - Update `packages/bridge-status-controller/CHANGELOG.md` with the
Mobile crash fix.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
f26118a8174554e73d576205f532dd0b6264ec77. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### packages/bridge-status-controller/CHANGELOG.md
```diff
@@ -12,6 +12,10 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 - Bump `@metamask/network-controller` from `^24.2.2` to `^24.3.0` ([#6883](https://github.com/MetaMask/core/pull/6883))
 - Bump `@metamask/transaction-controller` from `^60.7.0` to `^60.8.0` ([#6883](https://github.com/MetaMask/core/pull/6883))
 
+### Fixed
+
+- Fix issue with Mobile where app would crash after a successful tx ([#6890](https://github.com/MetaMask/core/pull/6890))
+
 ## [51.0.0]
 
 ### Changed
```

### packages/bridge-status-controller/src/utils/swap-received-amount.ts
```diff
@@ -44,7 +44,7 @@ const getReceivedERC20Amount = (
   const tokenTransferLog = txReceipt.logs.find((txReceiptLog) => {
     const isTokenTransfer =
       txReceiptLog.topics &&
-      txReceiptLog.topics[0].startsWith(TOKEN_TRANSFER_LOG_TOPIC_HASH);
+      txReceiptLog.topics[0]?.startsWith(TOKEN_TRANSFER_LOG_TOPIC_HASH);
     const isTransferFromGivenToken =
       txReceiptLog.address?.toLowerCase() ===
       quote.destAsset.address?.toLowerCase();
```
