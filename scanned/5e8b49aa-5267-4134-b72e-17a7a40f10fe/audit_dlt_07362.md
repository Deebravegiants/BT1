# [?] fix: Fix migration crash (#46632)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-09-24
Source: https://github.com/MetaMask/metamask-extension/commit/ce5346e20e5b060df768e1c876e95ddd122d35aa
Type: security-commit

## Details
fix: Fix migration crash (#46632)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

Opening the wallet crashed with `new BigNumber() not a number:
5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` (Solana mainnet CAIP reference). The
crash was in the unified-assets migration selectors in
`shared/lib/selectors/assets-migration.ts`, which remap `assetsBalance`
onto the legacy EVM controllers.

Those selectors filtered EVM accounts, then treated every asset under
them as EVM and passed the CAIP chain reference to
`decimalToPrefixedHex`. A Solana native asset stored under an EVM
account made that call throw and the UI error boundary took over.

This PR skips any asset whose CAIP namespace is not `eip155` before the
hex conversion, matching the other selectors in the same file.

## **Changelog**

CHANGELOG entry: Fixed a crash that occurred when unified asset state
included a non-EVM asset on an EVM account

## **Related issues**

Fixes: #46636

## **Manual testing steps**

1. Build and load the extension with unified assets enabled
(`ASSETS_UNIFIED_STATE_ENABLED` and the remote flag).
2. Unlock a wallet that has both an EVM account and Solana assets (or
state where a Solana native asset is present under an EVM account in
`assetsBalance`).
3. Open the home screen.
4. Confirm the wallet home renders and does not show "Your information
can't be shown".
5. Confirm ETH / EVM balances still display.

<!--
## **Screenshots/Recordings**
### **Before**
### **After**
-->

## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [x] I’ve included tests if applicable
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [x] I’ve applied the right labels on the PR (see [labeling
guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [x] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [x] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Medium Risk**
> Touches home-screen balance/token selectors on the unified-assets
path; the change is narrow defensive filtering with new regression
tests, but incorrect filtering could hide or mis-map balances.
> 
> **Overview**
> Fixes a wallet crash when unified asset state includes **non-EVM
assets (e.g. Solana) on an EVM account** in `assetsBalance`. The
unified-assets migration selectors in `assets-migration.ts` already
limited work to EVM accounts but still ran every asset through EVM-only
steps like `decimalToPrefixedHex`, which throws on Solana CAIP chain
references.
> 
> **Account tracker, tokens, and token-balances** migration selectors
now **skip assets whose CAIP namespace is not `eip155`** before hex
conversion and legacy controller shaping, consistent with other filters
in the same module.
> 
> Unit tests cover Solana native/token balances attached to an
`eip155:eoa` account and assert only EVM data is emitted without
throwing.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
70f54773f1c25c235545cdb094c2078ea4319031. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### shared/lib/selectors/assets-migration.test.ts
```diff
@@ -66,6 +66,8 @@ const erc20AssetAddressChecksummed = toChecksumHexAddress(
 const erc20AssetId = `eip155:1/erc20:${erc20AssetAddressLowercase}`;
 const solanaTokenAssetId =
   'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/token:EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v';
+const solanaNativeAssetId =
+  'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/slip44:501';
 
 const tempoChainId = '0x1079';
 const tempoPathUsdAddressLowercase: Hex =
@@ -429,6 +431,46 @@ describe('getAccountTrackerControllerAccountsByChainId', () => {
         '0x3a98',
       );
     });
+
+    it('skips a non-EVM native asset stored under an EVM account', () => {
+      const state = {
+        metamask: {
+          ...enabledFlags,
+          accountsByChainId: {},
+          assetsInfo: {
+            [nativeEthAssetId]: { type: 'native', decimals: 18 },
+            [solanaNativeAssetId]: { type: 'native', decimals: 9 },
+          },
+          assetsBalance: {
+            [mockAccountId]: {
+              [nativeEthAssetId]: { amount: '1' },
+              [solanaNativeAssetId]: { amount: '2' },
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
+      expect(() =>
+        getAccountTrackerControllerAccountsByChainId(state),
+      ).not.toThrow();
+      const result = getAccountTrackerControllerAccountsByChainId(state);
+      expect(result).toStrictEqual({
+        '0x1': {
+          [mockAccountAddressChecksummed]: {
+            balance: '0xde0b6b3a7640000',
+          },
+        },
+      });
+    });
   });
 });
 
@@ -669,6 +711,62 @@ describe('getTokensControllerAllTokens', () => {
 
       expect(result).toStrictEqual({});
     });
+
+    it('skips a non-EVM token stored under an EVM account', () => {
+      const state = {
+        metamask: {
+          ...enabledFlags,
+          allTokens: {},
+          allIgnoredTokens: {},
+          assetsInfo: {
+            [erc20AssetId]: {
+              type: 'erc20',
+              decimals: 6,
+              symbol: 'USDC',
+              name: 'USD Coin',
+            },
+            [solanaTokenAssetId]: {
+              type: 'spl',
+              decimals: 6,
+              symbol: 'USDC',
+              name: 'USD Coin',
+            },
+          },
+          assetsBalance: {
+            [mockAccountId]: {
+              [erc20AssetId]: { amount: '1' },
+              [solanaTokenAssetId]: { amount: '2' },
+            },
+          },
+          customAssets: {},
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
+      expect(() => getTokensControllerAllTokens(state)).not.toThrow();
+      const result = getTokensControllerAllTokens(state);
+      expect(result).toStrictEqual({
+        '0x1': {
+          [mockAccountAddressLowercase]: [
+            {
+              address: erc20AssetAddressChecksummed,
+              symbol: 'USDC',
+              decimals: 6,
+              name: 'USD Coin',
+              image: undefined,
+            },
+          ],
+        },
+      });
+    });
   });
 });
 
@@ -1003,6 +1101,47 @@ describe('getTokenBalancesControllerTokenBalances', () => {
       ).toStrictEqual([nativeAddress]);
     });
 
+    it('skips a non-EVM asset stored under an EVM account', () => {
+      const state = {
+        metamask: {
+          ...enabledFlags,
+          tokenBalances: {},
+          assetsInfo: {
+            [nativeEthAssetId]: { type: 'native', decimals: 18 },
+            [solanaNativeAssetId]: { type: 'native', decimals: 9 },
+          },
+          assetsBalance: {
+            [mockAccountId]: {
+              [nativeEthAssetId]: { amount: '1' },
+              [solanaNativeAssetId]: { amount: '2' },
+            },
+          },
+          customAssets: {},
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
+      expect(() =>
+        getTokenBalancesControllerTokenBalances(state),
+      ).not.toThrow();
+      const result = getTokenBalancesControllerTokenBalances(state);
+      const nativeAddress = getNativeAssetForChainId('0x1').address;
+      expect(Object.keys(result[mockAccountAddressLowercase])).toStrictEqual([
+        '0x1',
+      ]);
+      expect(
+        Object.keys(result[mockAccountAddressLowercase]['0x1']),
+      ).toStrictEqual([nativeAddress]);
+    });
+
     it('handles multiple EVM accounts', () => {
       const state = {
         metamask: {
@@ -2442,8 +2581,6 @@ describe('getMultichainAssetsRatesControllerConversionRates', () => {
 });
 
 describe('getRatesControllerRates', () => {
-  const solanaNativeAssetId =
-    'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/slip44:501';
   const solanaSplMissingSymbolAssetId =
     'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/token:2NzMQx8TiDFbw5p3oMNVBh59UkKAPLHoa62YV6vXNmmG';
 
```

### shared/lib/selectors/assets-migration.ts
```diff
@@ -158,7 +158,10 @@ export const getAccountTrackerControllerAccountsByChainId =
             assetId as CaipAssetType,
           );
 
-          // No need to check if the chain is EVM, we already filtered out non-EVM accounts
+          if (parsedChain.namespace !== KnownCaipNamespace.Eip155) {
+            continue;
+          }
+
           const hexChainId = decimalToPrefixedHex(parsedChain.reference);
           const amount = balanceData?.amount ?? '0';
 
@@ -237,7 +240,10 @@ export const getTokensControllerAllTokens = createDeepEqualSelector(
 
         const assetType = parseCaipAssetType(assetId);
 
-        // No need to check if the chain is EVM, we already filtered out non-EVM accounts
+        if (assetType.chain.namespace !== KnownCaipNamespace.Eip155) {
+          continue;
+        }
+
         const hexChainId = decimalToPrefixedHex(assetType.chain.reference);
         const assetAddress = toChecksumHexAddress(assetType.assetReference);
 
@@ -361,6 +367,10 @@ export const getTokenBalancesControllerTokenBalances = createDeepEqualSelector(
 
         const assetType = parseCaipAssetType(assetId as CaipAssetType);
 
+        if (assetType.chain.namespace !== KnownCaipNamespace.Eip155) {
+          continue;
+        }
+
         const hexChainId = decimalToPrefixedHex(assetType.chain.reference);
         const assetAddress = toChecksumHexAddress(
           metadata.type === 'native'
```
