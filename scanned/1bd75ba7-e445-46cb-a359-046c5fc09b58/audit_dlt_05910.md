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

If this PR is End-User-Facing, please write a short User-Facing
description in the past tense like:
`CHANGELOG entry: Added a new tab for users to see their NFTs`
`CHANGELOG entry: Fixed a bug that was causing some NFTs to flicker`

(This helps the Release Engineer do their job more quickly and
accurately)
-->

CHANGELOG entry: handle scientific notation in parseBalanceWithDecimals
to prevent BigInt crash

## **Related issues**

Fixes:

## **Manual testing steps**

1. Go to this page...
2.
3.

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

<!-- [screenshots/recordings] -->

### **After**

<!-- [screenshots/recordings] -->

## **Pre-merge author checklist**

- [ ] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding

Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [ ] I've completed the PR template to the best of my ability
- [ ] I’ve included tests if applicable
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [ ] I’ve applied the right labels on the PR (see [labeling

guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [ ] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [ ] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Medium Risk**
> Changes how native and token hex balances are derived for the
assets-unify migration path; wrong parsing would show incorrect
balances, though scope is limited and covered by new tests.
> 
> **Overview**
> Fixes **`BigInt` crashes** when unified asset balance strings arrive
in **scientific notation** (e.g. `"1e-18"` from very small amounts),
which the old decimal-splitting logic mangled into invalid strings.
> 
> Adds **`parseScientificNotationBalance`** and branches
**`parseBalanceWithDecimals`** on `e`/`E` before the fixed-point path,
converting to base units with **truncation toward zero** and **clamping
negatives to `0x0`**. Selector tests cover tiny balances, huge
exponents, and positive forms like `"1.5e2"`.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
dfbb13fd247a927874089de30b0beee055037ad3. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->
[e822338](https://github.com/MetaMask/metamask-extension/commit/e822338584d058972c00f4e48f84de91c6ad0dd0)

Co-authored-by: Salim TOUBAL <salim.toubal@outlook.com>

### shared/lib/selectors/assets-migration.test.ts
```diff
@@ -324,6 +324,107 @@ describe('getAccountTrackerControllerAccountsByChainId', () => {
       // 1.23456 with 2 decimals → truncated to 1.23 → 123
       expect(result['0x1'][mockAccountAddressChecksummed].balance).toBe('0x7b');
     });
+
+    it('does not crash when amount is in scientific notation (e.g. "1e-18")', () => {
+      const state = {
+        metamask: {
+          ...enabledFlags,
+          accountsByChainId: {},
+          assetsInfo: {
+            [nativeEthAssetId]: { type: 'native', decimals: 18 },
+          },
+          assetsBalance: {
+            [mockAccountId]: {
+              [nativeEthAssetId]: { amount: '1e-18' },
+            },
+          },
+          internalAccounts: {
+            accounts: {
+              [mockAccountId]: {
+                id: mockAccountId,
+                address: mockAccountAddressLowercase,
+                type: 'eip155:eoa',
+              },
+            },
+          },
+        },
+      };
+
+      // Should not throw — 1e-18 ETH = 1 wei = 0x1
+      expect(() =>
+        getAccountTrackerControllerAccountsByChainId(state),
+      ).not.toThrow();
+      const result = getAccountTrackerControllerAccountsByChainId(state);
+      expect(result['0x1'][mockAccountAddressChecksummed].balance).toBe('0x1');
+    });
+
+    it('does not crash when amount has absurd scientific notation exponent (e.g. "1e-18000000000000000000")', () => {
+      const state = {
+        metamask: {
+          ...enabledFlags,
+          accountsByChainId: {},
+          assetsInfo: {
+            [nativeEthAssetId]: { type: 'native', decimals: 18 },
+          },
+          assetsBalance: {
+            [mockAccountId]: {
+              [nativeEthAssetId]: { amount: '1e-18000000000000000000' },
+            },
+          },
+          internalAccounts: {
+            accounts: {
+              [mockAccountId]: {
+                id: mockAccountId,
+                address: mockAccountAddressLowercase,
+                type: 'eip155:eoa',
+              },
+            },
+          },
+        },
+      };
+
+      // Should not throw — value is sub-unit, rounds to 0x0
+      expect(() =>
+        getAccountTrackerControllerAccountsByChainId(state),
+      ).not.toThrow();
+      const result = getAccountTrackerControllerAccountsByChainId(state);
+      expect(result['0x1'][mockAccountAddressChecksummed].balance).toBe('0x0');
+    });
+
+    it('correctly parses positive scientific notation (e.g. "1.5e2" with 2 decimals)', () => {
+      const state = {
+        metamask: {
+          ...enabledFlags,
+          accountsByChainId: {},
+          assetsInfo: {
+            [nativeEthAssetId]: { type: 'native', decimals: 2 },
+          },
+          assetsBalance: {
+            [mockAccountId]: {
+              [nativeEthAssetId]: { amount: '1.5e2' },
+            },
+          },
+          internalAccounts: {
+            accounts: {
+              [mockAccountId]: {
+                id: mockAccountId,
+                address: mockAccountAddressLowercase,
+                type: 'eip155:eoa',
+              },
+            },
+          },
+        },
+      };
+
+      // 1.5e2 = 150 human-readable, with 2 decimals → 15000 base units = 0x3a98
+      expect(() =>
+        getAccountTrackerControllerAccountsByChainId(state),
+      ).not.toThrow();
+      const result = getAccountTrackerControllerAccountsByChainId(state);
+      expect(result['0x1'][mockAccountAddressChecksummed].balance).toBe(
+        '0x3a98',
+      );
+    });
   });
 });
 
```

### shared/lib/selectors/assets-migration.ts
```diff
@@ -945,10 +945,56 @@ export const getRatesControllerFiatCurrency = createDeepEqualSelector(
   },
 ) as unknown as ControllerStateSelector<RatesControllerState, 'fiatCurrency'>;
 
+/**
+ * Converts a scientific notation balance string (e.g. "1e-18") to its raw
+ * base-unit bigint representation given the token's decimal precision.
+ * Sub-unit values are truncated toward zero (e.g. "1e-19" with 18 decimals
+ * yields 0n). Returns 0n for any string that is not valid scientific notation.
+ *
+ * @param balanceString - The balance in scientific notation (e.g. "1e-18").
+ * @param decimals - The token's decimal precision.
+ * @returns The raw base-unit value as a bigint.
+ */
+function parseScientificNotationBalance(
+  balanceString: string,
+  decimals: number,
+): bigint {
+  const match = balanceString.match(/^([+-]?\d+(?:\.\d+)?)[eE]([+-]?\d+)$/u);
+  if (!match) {
+    return 0n;
+  }
+
+  const [, coefficient, rawExponent] = match;
+  const exponent = parseInt(rawExponent, 10);
+  const isNegative = coefficient.startsWith('-');
+  const absCoefficient = coefficient.replace(/^[+-]/u, '');
+  const [coefInt, coefFrac = ''] = absCoefficient.split('.');
+  const coefDigits = coefInt + coefFrac;
+  const finalExponent = exponent + decimals - coefFrac.length;
+
+  let result: bigint;
+  if (finalExponent >= 0) {
+    result = BigInt(coefDigits) * 10n ** BigInt(finalExponent);
+  } else {
+    // Fractional base units are truncated by keeping only the leading digits.
+    const digitsToKeep = coefDigits.length + finalExponent;
+    result = digitsToKeep <= 0 ? 0n : BigInt(coefDigits.slice(0, digitsToKeep));
+  }
+
+  return isNegative ? -result : result;
+}
+
 function parseBalanceWithDecimals(
   balanceString: string,
   decimals: number,
 ): Hex {
+  // Scientific notation (e.g. "1e-18") cannot be split on "." correctly —
+  // handle it separately before the normal fixed-point path.
+  if (balanceString.includes('e') || balanceString.includes('E')) {
+    const raw = parseScientificNotationBalance(balanceString, decimals);
+    return bigIntToHex(raw < 0n ? 0n : raw);
+  }
+
   const [integerPart, fractionalPart = ''] = balanceString.split('.');
 
   if (decimals === 0) {
@@ -963,9 +1009,7 @@ function parseBalanceWithDecimals(
 
   return bigIntToHex(
     BigInt(
-      `${integerPart}${fractionalPart}${'0'.repeat(
-        decimals - fractionalPart.length,
-      )}`,
+      `${integerPart}${fractionalPart}${'0'.repeat(decimals - fractionalPart.length)}`,
     ),
   );
 }
```
