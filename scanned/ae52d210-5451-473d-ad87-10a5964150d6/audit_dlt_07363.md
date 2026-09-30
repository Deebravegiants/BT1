# [?] fix: external account bridges cause app to crash (#41442)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-04-07
Source: https://github.com/MetaMask/metamask-extension/commit/17f92a68d70a499fcbb6d6de4a3b73245e614567
Type: security-commit

## Details
fix: external account bridges cause app to crash (#41442)

## **Description**

When a user performs an EVM ↔ non-EVM bridge and selects a custom
recipient address that is not derived from their SRP (labeled "External
account"), the extension crashes with `TypeError: Cannot read properties
of undefined (reading 'id')`.

The root cause is that `getAccountGroupsByAddress` returns an empty
array for addresses not belonging to any wallet account group.
Destructuring `const [accountGroup] = []` yields `undefined`, and
subsequent accesses to `accountGroup.id` crash in three locations:

- `BridgeAssetPicker` component (`getBridgeSortedAssets` call and
`useMemo` deps)
- `usePopularTokens` hook (`getBridgeAssetsByAssetId` call)
- `useTokenSearchResults` hook (`getBridgeAssetsByAssetId` call)

The fix adds a guard check before accessing `accountGroup.id` in all
three locations, returning safe empty defaults (`[]` or `{}`) when no
matching account group exists. Tests are added to cover this scenario.

## **Changelog**

CHANGELOG entry: Fixed a crash when selecting an external recipient
address during cross-chain bridge transactions

## **Related issues**

Fixes: https://consensyssoftware.atlassian.net/browse/SWAPS-4264

## **Manual testing steps**

1. Open MetaMask and navigate to the Bridge page
2. Set up an EVM to non-EVM bridge (e.g., Ethereum → Solana)
3. Click the Recipient field and enter an external address not generated
from your SRP
4. Select the external account record that appears in the dropdown
5. Verify the app does not crash and the bridge page remains usable

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
- [x] I've included tests if applicable
- [x] I've documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [x] I've applied the right labels on the PR (see [labeling
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
> **Low Risk**
> Low risk defensive changes that add `undefined` handling around bridge
asset lookups for external addresses, plus targeted unit tests. Main
risk is minor behavior changes where selectors now return empty results
instead of throwing when no account group is found.
> 
> **Overview**
> Prevents bridge UI crashes when the selected address is *external*
(not part of any account group) by making `accountGroup.id` access safe
across the asset picker and token-list hooks.
> 
> Bridge asset selectors now short-circuit on missing `accountGroupId`
and return empty defaults, and new unit tests cover the undefined-group
scenario for
`getBridgeSortedAssets`/`getBridgeAssetsByAssetId`/`getBridgeBalancesByChainId`,
`usePopularTokens`, and `useTokenSearchResults`.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
79a3c095e2b999b4a049ef7192dcda611ec6d7c2. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### test/data/bridge/mock-bridge-store.ts
```diff
@@ -169,6 +169,9 @@ export const MOCK_BITCOIN_ACCOUNT = {
   },
 };
 
+export const MOCK_EXTERNAL_SOLANA_ADDRESS =
+  '8sKQHfjNhvmAw94PhfvfMcytmqW6jmxvwieYyzXCCPu';
+
 export const createBridgeMockStore = ({
   featureFlagOverrides = { bridgeConfig: {} },
   bridgeSliceOverrides = {},
```

### test/jest/console-baseline-unit.json
```diff
@@ -568,6 +568,14 @@
     "ui/hooks/accounts/useAccountsOperationsLoadingStates.test.ts": {
       "MetaMask: Background connection not initialized": 2
     },
+    "ui/hooks/bridge/usePopularTokens.test.ts": {
+      "React: Act warnings (component updates not wrapped)": 16,
+      "Reselect: Input stability warnings": 1
+    },
+    "ui/hooks/bridge/useTokenSearchResults.test.ts": {
+      "React: Act warnings (component updates not wrapped)": 2,
+      "Reselect: Input stability warnings": 1
+    },
     "ui/hooks/gator-permissions/useGatorPermissionTokenInfo.test.tsx": {
       "React: Act warnings (component updates not wrapped)": 10,
       "Reselect: Identity function warnings": 1
```

### ui/ducks/bridge/asset-selectors.test.ts
```diff
@@ -267,5 +267,38 @@ describe('Bridge asset selectors', () => {
         }
       `);
     });
+
+    it('returns empty results when accountGroupId is undefined', () => {
+      const state = createBridgeMockStore({
+        featureFlagOverrides: {
+          bridgeConfig: {
+            refreshRate: 30000,
+            priceImpactThreshold: {
+              normal: 1,
+              gasless: 2,
+            },
+            maxRefreshCount: 5,
+            support: true,
+            chains: {
+              [CHAIN_IDS.MAINNET]: {
+                isActiveSrc: true,
+                isActiveDest: true,
+              },
+            },
+            chainRanking: [{ chainId: formatChainIdToCaip(CHAIN_IDS.MAINNET) }],
+          },
+        },
+      });
+
+      // Simulate the caller pattern: accountGroup is undefined when address has no matching group
+      const [accountGroup] = getAccountGroupsByAddress(state, [
+        'non-existent-address',
+      ]);
+      expect(accountGroup).toBeUndefined();
+
+      expect(getBridgeSortedAssets(state, accountGroup?.id)).toEqual([]);
+      expect(getBridgeAssetsByAssetId(state, accountGroup?.id)).toEqual({});
+      expect(getBridgeBalancesByChainId(state, accountGroup?.id)).toEqual({});
+    });
   });
 });
```

### ui/ducks/bridge/asset-selectors.ts
```diff
@@ -31,6 +31,7 @@ import {
   getAssetsRates,
 } from '../../selectors/assets';
 import { getInternalAccountByGroupAndCaip } from '../../selectors/multichain-accounts/account-tree';
+import { EMPTY_ARRAY } from '../../selectors/shared';
 import { type BridgeAppState, getFromChains } from './selectors';
 import { type BridgeToken } from './types';
 import { getMaybeHexChainId } from './utils';
@@ -317,17 +318,23 @@ const getNonEvmAssetsWithBalance = createSelector(
 // Combines EVM and non-EVM assets and appends tokenFiatAmount to each asset
 const getBridgeAssetsForAccountGroupId = createSelector(
   [
+    (_: BridgeAppState, id: AccountGroupId | undefined) => id,
     getEvmAssetsWithBalance,
     getEvmExchangeRates,
     getNonEvmAssetsWithBalance,
     getAssetsRates,
   ],
   (
+    id,
     evmAssetsWithBalance,
     evmExchangeRatesByAssetId,
     nonEvmAssetsWithBalance,
     nonEvmExchangeRatesByAssetId,
   ): BridgeToken[] => {
+    if (!id) {
+      return EMPTY_ARRAY as unknown as BridgeToken[];
+    }
+
     const evmAssetsWithFiatBalances = evmAssetsWithBalance.map((asset) => ({
       ...asset,
       tokenFiatAmount: new BigNumber(asset.balance ?? '0')
```

### ui/hooks/bridge/usePopularTokens.test.ts
```diff
@@ -0,0 +1,86 @@
+import { formatChainIdToCaip } from '@metamask/bridge-controller';
+import { renderHookWithProvider } from '../../../test/lib/render-helpers-navigate';
+import { CHAIN_IDS } from '../../../shared/constants/network';
+import {
+  createBridgeMockStore,
+  MOCK_EVM_ACCOUNT,
+  MOCK_EXTERNAL_SOLANA_ADDRESS,
+} from '../../../test/data/bridge/mock-bridge-store';
+import { usePopularTokens } from './usePopularTokens';
+
+jest.mock('../../pages/bridge/utils/tokens', () => ({
+  fetchPopularTokens: jest.fn().mockResolvedValue([]),
+}));
+
+jest.mock('../../store/actions', () => ({
+  getBearerToken: jest.fn().mockResolvedValue('mock-jwt'),
+}));
+
+describe('usePopularTokens', () => {
+  it('does not crash when accountAddress is an external address with no matching account group', () => {
+    const mockStoreState = createBridgeMockStore({
+      featureFlagOverrides: {
+        bridgeConfig: {
+          refreshRate: 30000,
+          maxRefreshCount: 5,
+          support: true,
+          chains: {
+            [CHAIN_IDS.MAINNET]: {
+              isActiveSrc: true,
+              isActiveDest: true,
+            },
+          },
+          chainRanking: [{ chainId: formatChainIdToCaip(CHAIN_IDS.MAINNET) }],
+        },
+      },
+    });
+
+    const { result } = renderHookWithProvider(
+      () =>
+        usePopularTokens({
+          assetsToInclude: [],
+          accountAddress: MOCK_EXTERNAL_SOLANA_ADDRESS,
+          chainIds: new Set([formatChainIdToCaip(CHAIN_IDS.MAINNET)]),
+        }),
+      mockStoreState,
+    );
+
+    expect(result.current.popularTokensList).toEqual([]);
+    expect(result.current.isLoading).toBe(true);
+  });
+
+  it('returns owned assets when accountAddress belongs to a known account group', () => {
+    const mockStoreState = createBridgeMockStore({
+      featureFlagOverrides: {
+        bridgeConfig: {
+          refreshRate: 30000,
+          maxRefreshCount: 5,
+          support: true,
+          chains: {
+            [CHAIN_IDS.MAINNET]: {
+              isActiveSrc: true,
+              isActiveDest: true,
+            },
+          },
+          chainRanking: [{ chainId: formatChainIdToCaip(CHAIN_IDS.MAINNET) }],
+        },
+      },
+    });
+
+    const { result } = renderHookWithProvider(
+      () =>
+        usePopularTokens({
+          assetsToInclude: [],
+          accountAddress: MOCK_EVM_ACCOUNT.address,
+          chainIds: new Set([formatChainIdToCaip(CHAIN_IDS.MAINNET)]),
+        }),
+      mockStoreState,
+    );
+
+    // The hook resolves the account group and calls getBridgeAssetsByAssetId
+    // (truthy branch of: accountGroup ? getBridgeAssetsByAssetId(...) : {})
+    // popularTokensList falls back to assetsToInclude while token list loads
+    expect(result.current.popularTokensList).toEqual([]);
+    expect(result.current.isLoading).toBe(true);
+  });
+});
```

### ui/hooks/bridge/usePopularTokens.ts
```diff
@@ -37,7 +37,7 @@ export const usePopularTokens = ({
     getAccountGroupsByAddress(state, [accountAddress]),
   );
   const ownedAssetsByAssetId = useSelector((state: BridgeAppState) =>
-    getBridgeAssetsByAssetId(state, accountGroup.id),
+    getBridgeAssetsByAssetId(state, accountGroup?.id),
   );
 
   const abortControllerRef = useRef<AbortController | null>(null);
```

### ui/hooks/bridge/useTokenSearchResults.test.ts
```diff
@@ -0,0 +1,94 @@
+import { formatChainIdToCaip } from '@metamask/bridge-controller';
+import { renderHookWithProvider } from '../../../test/lib/render-helpers-navigate';
+import { CHAIN_IDS } from '../../../shared/constants/network';
+import {
+  createBridgeMockStore,
+  MOCK_EVM_ACCOUNT,
+  MOCK_EXTERNAL_SOLANA_ADDRESS,
+} from '../../../test/data/bridge/mock-bridge-store';
+import { useTokenSearchResults } from './useTokenSearchResults';
+
+jest.mock('../../pages/bridge/utils/tokens', () => ({
+  fetchTokensBySearchQuery: jest.fn().mockResolvedValue({
+    tokens: [],
+    endCursor: undefined,
+    hasNextPage: false,
+  }),
+}));
+
+jest.mock('../../store/actions', () => ({
+  getBearerToken: jest.fn().mockResolvedValue('mock-jwt'),
+}));
+
+describe('useTokenSearchResults', () => {
+  it('does not crash when accountAddress is an external address with no matching account group', () => {
+    const mockStoreState = createBridgeMockStore({
+      featureFlagOverrides: {
+        bridgeConfig: {
+          refreshRate: 30000,
+          maxRefreshCount: 5,
+          support: true,
+          chains: {
+            [CHAIN_IDS.MAINNET]: {
+              isActiveSrc: true,
+              isActiveDest: true,
+            },
+          },
+          chainRanking: [{ chainId: formatChainIdToCaip(CHAIN_IDS.MAINNET) }],
+        },
+      },
+    });
+
+    const { result } = renderHookWithProvider(
+      () =>
+        useTokenSearchResults({
+          searchQuery: '',
+          assetsToInclude: [],
+          accountAddress: MOCK_EXTERNAL_SOLANA_ADDRESS,
+          chainIds: new Set([formatChainIdToCaip(CHAIN_IDS.MAINNET)]),
+        }),
+      mockStoreState,
+    );
+
+    expect(result.current.searchResults).toEqual([]);
+    expect(result.current.isSearchResultsLoading).toBe(false);
+    expect(result.current.hasMoreResults).toBe(false);
+  });
+
+  it('returns empty search results when accountAddress belongs to a known account group', () => {
+    const mockStoreState = createBridgeMockStore({
+      featureFlagOverrides: {
+        bridgeConfig: {
+          refreshRate: 30000,
+          maxRefreshCount: 5,
+          support: true,
+          chains: {
+            [CHAIN_IDS.MAINNET]: {
+              isActiveSrc: true,
+              isActiveDest: true,
+            },
+          },
+          chainRanking: [{ chainId: formatChainIdToCaip(CHAIN_IDS.MAINNET) }],
+        },
+      },
+    });
+
+    const { result } = renderHookWithProvider(
+      () =>
+        useTokenSearchResults({
+          searchQuery: '',
+          assetsToInclude: [],
+          accountAddress: MOCK_EVM_ACCOUNT.address,
+          chainIds: new Set([formatChainIdToCaip(CHAIN_IDS.MAINNET)]),
+        }),
+      mockStoreState,
+    );
+
+    // The hook resolves the account group and calls getBridgeAssetsByAssetId
+    // (truthy branch of: accountGroup ? getBridgeAssetsByAssetId(...) : {})
+    // No search query → no fetch triggered, empty results
+    expect(result.current.searchResults).toEqual([]);
+    expect(result.current.isSearchResultsLoading).toBe(false);
+    expect(result.current.hasMoreResults).toBe(false);
+  });
+});
```

### ui/hooks/bridge/useTokenSearchResults.ts
```diff
@@ -37,7 +37,7 @@ export const useTokenSearchResults = ({
     getAccountGroupsByAddress(state, [accountAddress]),
   );
   const ownedAssetsByAssetId = useSelector((state: BridgeAppState) =>
-    getBridgeAssetsByAssetId(state, accountGroup.id),
+    getBridgeAssetsByAssetId(state, accountGroup?.id),
   );
 
   const abortControllerRef = useRef<AbortController>(new AbortController());
```

### ui/pages/bridge/prepare/components/bridge-asset-picker/index.tsx
```diff
@@ -78,7 +78,7 @@ export const BridgeAssetPicker = ({
     getAccountGroupsByAddress(state, [accountAddress]),
   );
   const assetsWithBalance = useSelector((state: BridgeAppState) =>
-    getBridgeSortedAssets(state, accountGroup.id),
+    getBridgeSortedAssets(state, accountGroup?.id),
   );
 
   const t = useI18nContext();
@@ -117,7 +117,7 @@ export const BridgeAssetPicker = ({
         (a) => a.assetId?.toLowerCase(),
       ).map((token) => toBridgeToken(token)),
     // Ignore warnings about assetsWithBalance to prevent re-fetching token list excessively
-    [chainIdsSet, accountGroup.id, accountAddress],
+    [chainIdsSet, accountGroup?.id, accountAddress],
   );
 
   const { popularTokensList, isLoading: isPopularTokensLoading } =
```
