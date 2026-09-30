# [?] prevent crash from missing account (#8604)

## Summary
Severity: Unknown
Chain: Tooling
Component: MetaMask/core
Published: 2026-04-28
Source: https://github.com/MetaMask/core/commit/fac6fa105223c4c43bd45674edab9efbe6e4c761
Type: security-commit

## Details
prevent crash from missing account (#8604)

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

Stop crash that occurs when there is a missing entry in the
`internalAccount` object.


https://metamask.sentry.io/issues/7394639158/?project=273505&query=is%3Aunresolved%20Cannot%20read%20properties%20of%20undefined&referrer=issue-stream

https://metamask.sentry.io/issues/6977774458/?project=273505&query=is%3Aunresolved%20Cannot%20read%20properties%20of%20undefined&referrer=issue-stream

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

## Checklist

- [X] I've updated the test suite for new or updated code as appropriate
- [X] I've updated documentation (JSDoc, Markdown, etc.) for new or
updated code as appropriate
- [X] I've communicated my changes to consumers by [updating changelogs
for packages I've
changed](https://github.com/MetaMask/core/tree/main/docs/processes/updating-changelogs.md)
- [X] I've introduced [breaking
changes](https://github.com/MetaMask/core/tree/main/docs/processes/breaking-changes.md)
in this PR and have prepared draft pull requests for clients and
consumer packages to resolve them


<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Small defensive change in a selector plus a unit test; behavior only
changes for inconsistent state where an account ID is missing.
> 
> **Overview**
> Prevents `selectAssetsBySelectedAccountGroup` from crashing when an
`accountTree` group references an account ID that is missing from
`internalAccounts` by skipping those entries during account mapping.
> 
> Adds a regression test covering the missing-account scenario and
documents the fix in the assets-controllers changelog.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
78aa9aa0ff4107b685c534bf9af01967c791c703. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### packages/assets-controllers/CHANGELOG.md
```diff
@@ -27,6 +27,10 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
   - Malicious tokens that slip through are caught by the periodic rescan (runs daily by default)
 - Bump `@metamask/transaction-controller` from `^64.3.0` to `^64.4.0` ([#8585](https://github.com/MetaMask/core/pull/8585))
 
+### Fixed
+
+- Fix `selectAssetsBySelectedAccountGroup` crashing when an account referenced in the account tree is missing from internal accounts ([#8604](https://github.com/MetaMask/core/pull/8604))
+
 ## [104.3.0]
 
 ### Added
```

### packages/assets-controllers/src/selectors/token-selectors.test.ts
```diff
@@ -877,6 +877,18 @@ describe('token-selectors', () => {
       expect(result).toStrictEqual(expectedMockResult);
     });
 
+    it('skips accounts referenced in accountTree but missing from internalAccounts', () => {
+      const state = cloneDeep(mockedMergedState);
+
+      state.accountTree.wallets['entropy:01K1TJY9QPSCKNBSVGZNG510GJ'].groups[
+        'entropy:01K1TJY9QPSCKNBSVGZNG510GJ/0'
+      ].accounts.push('non-existent-account-id');
+
+      const result = selectAssetsBySelectedAccountGroup(state);
+
+      expect(result).toStrictEqual(expectedMockResult);
+    });
+
     it('returns no tokens if there is no selected account group', () => {
       const result = selectAssetsBySelectedAccountGroup({
         ...mockedMergedState,
```

### packages/assets-controllers/src/selectors/token-selectors.ts
```diff
@@ -140,6 +140,10 @@ const selectAccountsToGroupIdMap = createAssetListSelector(
         for (const accountId of accounts) {
           const internalAccount = internalAccounts.accounts[accountId];
 
+          if (!internalAccount) {
+            continue;
+          }
+
           accountsMap[
             // TODO: We would not need internalAccounts if evmTokens state had the accountId
             internalAccount.type.startsWith('eip155')
```
