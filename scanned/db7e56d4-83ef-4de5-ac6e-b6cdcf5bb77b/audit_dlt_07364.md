# [?] fix(accounts): prevent crash when account tree references orphaned account IDs (#41405)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-04-02
Source: https://github.com/MetaMask/metamask-extension/commit/75594855ee20d606e7b579336b2afca3d1386365
Type: security-commit

## Details
fix(accounts): prevent crash when account tree references orphaned account IDs (#41405)

## **Description**

When state corruption occurs (e.g. after a wallet reset or Snap keyring
reset), the `accountTree` can contain account IDs that no longer exist
in `internalAccounts`. In `getWalletsWithAccounts`, spreading
`undefined` via `{ ...accountsById[missingId] }` produces an empty
object with no `address` property. Downstream,
`getWalletIdAndNameByAccountAddress` then calls `.toLowerCase()` on
`undefined`, crashing with:

```
TypeError: Cannot read properties of undefined (reading 'toLowerCase')
  at getWalletIdAndNameByAccountAddress (ui/selectors/multichain-accounts/account-tree.ts)
```

**Root cause:** The account tree references entropy source IDs that no
longer exist in the actual keyrings — typically after a user forgets
their password and uses the wallet reset flow, or after using Snaps.

**Fix:**
1. **`getWalletsWithAccounts`** — added a `.filter()` before `.map()` to
skip any account ID that has no entry in `accountsById`. This prevents
orphaned entries from ever entering the consolidated wallet data
structure.
2. **`getWalletIdAndNameByAccountAddress`** — added optional chaining
`acc.address?.toLowerCase()` as a defensive guard.
3. Three regression tests added to prevent future regressions.

## **Changelog**

CHANGELOG entry: Fixed a crash that could occur for users with corrupted
wallet state after a password reset or Snap keyring usage.

## **Related issues**

Fixes: #41141
Fixes: https://consensyssoftware.atlassian.net/browse/MUL-1633

## **Manual testing steps**

This bug is triggered by corrupted state, which is hard to reproduce
manually. The fix is covered by unit tests. To verify:

1. Run `yarn test:unit
ui/selectors/multichain-accounts/account-tree.test.ts` — all 75 tests
should pass.
2. Load the extension normally and verify the account list renders
without errors.

<!--
## **Screenshots/Recordings**

### **Before**

### **After**
-->

## **Pre-merge author checklist**

- [ ] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [ ] I've completed the PR template to the best of my ability
- [ ] I've included tests if applicable
- [ ] I've documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [ ] I've applied the right labels on the PR (see [labeling
guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [ ] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [ ] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

Made with [Cursor](https://cursor.com)

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk defensive change in selectors: it only filters out account
IDs that cannot be resolved to `internalAccounts`, preventing crashes in
downstream lookups. Main impact is that corrupted/stale entries will no
longer appear in consolidated wallet/group account lists.
> 
> **Overview**
> Prevents crashes when `accountTree` contains stale/orphaned account
IDs by filtering unresolved IDs out of `getWalletsWithAccounts` before
building the consolidated wallets/groups structure.
> 
> Adds regression tests covering: filtering orphaned IDs from groups,
`getWalletIdAndNameByAccountAddress` not throwing with corrupted state,
and returning `null` when all referenced accounts are orphaned.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
d7796094e9afb31cc34daa65c7173006c7b5f3d1. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### ui/selectors/multichain-accounts/account-tree.test.ts
```diff
@@ -260,6 +260,46 @@ describe('Multichain Accounts Selectors', () => {
   });
 
   describe('getWalletsWithAccounts', () => {
+    it('filters out account IDs that have no matching entry in internalAccounts (state corruption)', () => {
+      // Inject a stale/orphaned account ID into an existing group to simulate corruption
+      const corruptedState = {
+        ...typedMockState,
+        metamask: {
+          ...typedMockState.metamask,
+          accountTree: {
+            ...typedMockState.metamask.accountTree,
+            wallets: {
+              ...typedMockState.metamask.accountTree.wallets,
+              [ENTROPY_WALLET_1_ID]: {
+                ...typedMockState.metamask.accountTree.wallets[
+                  ENTROPY_WALLET_1_ID as unknown as keyof typeof typedMockState.metamask.accountTree.wallets
+                ],
+                groups: {
+                  [ENTROPY_GROUP_1_ID]: {
+                    ...typedMockState.metamask.accountTree.wallets[
+                      ENTROPY_WALLET_1_ID as unknown as keyof typeof typedMockState.metamask.accountTree.wallets
+                    ].groups[ENTROPY_GROUP_1_ID],
+                    accounts: [
+                      ACCOUNT_1_ID,
+                      'stale-orphaned-account-id-that-does-not-exist',
+                    ],
+                  },
+                },
+              },
+            },
+          },
+        },
+      } as unknown as typeof typedMockState;
+
+      expect(() => getWalletsWithAccounts(corruptedState)).not.toThrow();
+      const result = getWalletsWithAccounts(corruptedState);
+      const accounts =
+        result[ENTROPY_WALLET_1_ID]?.groups[ENTROPY_GROUP_1_ID]?.accounts;
+      // Orphaned account ID must be filtered out; only the valid account remains
+      expect(accounts).toHaveLength(1);
+      expect(accounts?.[0].id).toBe(ACCOUNT_1_ID);
+    });
+
     it('returns wallets with accounts and their metadata', () => {
       const result = getWalletsWithAccounts(typedMockState);
 
@@ -611,6 +651,72 @@ describe('Multichain Accounts Selectors', () => {
 
       expect(result).toBeNull();
     });
+
+    it('does not throw when the account tree references orphaned account IDs (state corruption)', () => {
+      const corruptedState = {
+        ...typedMockState,
+        metamask: {
+          ...typedMockState.metamask,
+          accountTree: {
+            ...typedMockState.metamask.accountTree,
+            wallets: {
+              ...typedMockState.metamask.accountTree.wallets,
+              [ENTROPY_WALLET_1_ID]: {
+                ...typedMockState.metamask.accountTree.wallets[
+                  ENTROPY_WALLET_1_ID as unknown as keyof typeof typedMockState.metamask.accountTree.wallets
+                ],
+                groups: {
+                  [ENTROPY_GROUP_1_ID]: {
+                    ...typedMockState.metamask.accountTree.wallets[
+                      ENTROPY_WALLET_1_ID as unknown as keyof typeof typedMockState.metamask.accountTree.wallets
+                    ].groups[ENTROPY_GROUP_1_ID],
+                    accounts: ['stale-orphaned-account-id-that-does-not-exist'],
+                  },
+                },
+              },
+            },
+          },
+        },
+      } as unknown as typeof typedMockState;
+
+      expect(() =>
+        getWalletIdAndNameByAccountAddress(corruptedState, ACCOUNT_1_ADDRESS),
+      ).not.toThrow();
+    });
+
+    it('returns null when all accounts in the tree are orphaned (state corruption)', () => {
+      const corruptedState = {
+        ...typedMockState,
+        metamask: {
+          ...typedMockState.metamask,
+          accountTree: {
+            ...typedMockState.metamask.accountTree,
+            wallets: {
+              ...typedMockState.metamask.accountTree.wallets,
+              [ENTROPY_WALLET_1_ID]: {
+                ...typedMockState.metamask.accountTree.wallets[
+                  ENTROPY_WALLET_1_ID as unknown as keyof typeof typedMockState.metamask.accountTree.wallets
+                ],
+                groups: {
+                  [ENTROPY_GROUP_1_ID]: {
+                    ...typedMockState.metamask.accountTree.wallets[
+                      ENTROPY_WALLET_1_ID as unknown as keyof typeof typedMockState.metamask.accountTree.wallets
+                    ].groups[ENTROPY_GROUP_1_ID],
+                    accounts: ['stale-orphaned-account-id-that-does-not-exist'],
+                  },
+                },
+              },
+            },
+          },
+        },
+      } as unknown as typeof typedMockState;
+
+      const result = getWalletIdAndNameByAccountAddress(
+        corruptedState,
+        ACCOUNT_1_ADDRESS,
+      );
+      expect(result).toBeNull();
+    });
   });
 
   describe('getInternalAccountByGroupAndCaip', () => {
```

### ui/selectors/multichain-accounts/account-tree.ts
```diff
@@ -127,22 +127,24 @@ export const getWalletsWithAccounts = createSelector(
         };
 
         Object.values(wallet.groups).forEach((group: AccountGroupObject) => {
-          const accountsFromGroup = group.accounts.map((accountId) => {
-            const accountWithMetadata = { ...accountsById[accountId] };
-
-            // Set flags for pinned, hidden, and active accounts
-            accountWithMetadata.pinned = pinnedAccountsSet.has(
-              accountWithMetadata.address,
-            );
-            accountWithMetadata.hidden = hiddenAccountsSet.has(
-              accountWithMetadata.address,
-            );
-            accountWithMetadata.active =
-              selectedAccount.id === accountWithMetadata.id &&
-              connectedAccountIdsSet.has(accountWithMetadata.id);
-
-            return accountWithMetadata;
-          });
+          const accountsFromGroup = group.accounts
+            .filter((accountId) => accountsById[accountId] !== undefined)
+            .map((accountId) => {
+              const accountWithMetadata = { ...accountsById[accountId] };
+
+              // Set flags for pinned, hidden, and active accounts
+              accountWithMetadata.pinned = pinnedAccountsSet.has(
+                accountWithMetadata.address,
+              );
+              accountWithMetadata.hidden = hiddenAccountsSet.has(
+                accountWithMetadata.address,
+              );
+              accountWithMetadata.active =
+                selectedAccount.id === accountWithMetadata.id &&
+                connectedAccountIdsSet.has(accountWithMetadata.id);
+
+              return accountWithMetadata;
+            });
 
           consolidatedWallets[wallet.id].groups[group.id] = {
             id: group.id,
```
