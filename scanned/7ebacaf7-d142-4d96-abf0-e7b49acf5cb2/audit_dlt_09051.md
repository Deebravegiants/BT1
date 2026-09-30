# [?] fix: cp-13.8.0 ensure asset price chart does not crash and uses correct time ranges (#37505)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2025-11-04
Source: https://github.com/MetaMask/metamask-extension/commit/0a1d33f26e314ecd70ca74f774abb1b2657d15cd
Type: security-commit

## Details
fix: cp-13.8.0 ensure asset price chart does not crash and uses correct time ranges (#37505)

## **Description**

Adds try/catch logic and defaults to EVM timeranges if fails to parse
CAIPAssetType.
Also ensures that we pass in CAIPAssetType into the `useChartTimeRanges`
hook to prevent potential future issues (due to invalid types).

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/37505?quickstart=1)

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

CHANGELOG entry: fix historical prices chart ranges for non-evm assets.

## **Related issues**

Fixes: https://github.com/MetaMask/metamask-extension/issues/37384

## **Manual testing steps**

Click BTC or SOL, observe charts - should not crash.

Testing missing chart data:
1. Click on "popular networks" filter
2. Click on BTC or SOL
3. Click 1W chart range
4. Expected - chart data should be visible

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

https://www.loom.com/share/adb371dd1bd24ca395632c28c20e02f5

<!-- [screenshots/recordings] -->

### **After**

https://www.loom.com/share/1d975fed43d04b35bd1b5d7f9d84c57b

<!-- [screenshots/recordings] -->

## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [x] I’ve included tests if applicable
- [x] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [x] I’ve applied the right labels on the PR (see [labeling
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
> Converts token addresses to CAIP asset types, passes them to the chart
hook, and updates the hook to infer EVM via CAIP with try/catch
fallbacks to default time ranges; adds corresponding tests.
> 
> - **Asset Chart (`ui/pages/asset/components/chart/asset-chart.tsx`)**:
> - Add `convertAddressToAssetCaipType` to normalize inputs (returns
CAIP as-is; builds EIP155 `erc20` from hex `address` + `chainId`; else
`undefined`).
> - Use `useMemo` to compute `caipAssetType` and pass to
`useChartTimeRanges`.
> - **Hook (`ui/pages/asset/hooks/useChartTimeRanges.ts`)**:
> - Infer EVM by parsing `caipAssetType` (namespace `eip155`); return
default ranges for EVM.
> - Wrap logic in try/catch; on errors or missing inputs, warn and
return default ranges.
> - For non-EVM, derive ranges from `historicalPrices`, filtering
invalid durations and sorting by length.
>   - Remove dependency on multichain EVM selector.
> - **Tests**:
> - Add `asset-chart.test.tsx` for `convertAddressToAssetCaipType` (CAIP
passthrough, EIP155 creation, invalid inputs).
> - Update `useChartTimeRanges.test.ts` to cover EVM defaults, missing
inputs defaults, and non-EVM behaviors (derive, filter, sort).
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
6eec95a0eb35ca1fae1b660195cbf6674c92f5dd. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### ui/pages/asset/components/chart/asset-chart.test.tsx
```diff
@@ -0,0 +1,38 @@
+import { convertAddressToAssetCaipType } from './asset-chart';
+
+describe('convertAddressToAssetCaipType', () => {
+  it('returns address unchanged when already a CAIP asset type', () => {
+    const address = 'eip155:1/erc20:0x6982508145454Ce325dDbE47a25d4ec3d2311933';
+    const chainId = '0x1';
+
+    const result = convertAddressToAssetCaipType(address, chainId);
+
+    expect(result).toBe(address);
+  });
+
+  it('creates EIP155 CAIP asset type for valid hex address and chainId', () => {
+    const address = '0x6982508145454Ce325dDbE47a25d4ec3d2311933';
+    const chainId = '0x1';
+
+    const result = convertAddressToAssetCaipType(address, chainId);
+
+    expect(result).toBe(
+      'eip155:1/erc20:0x6982508145454Ce325dDbE47a25d4ec3d2311933',
+    );
+  });
+
+  it('returns undefined for invalid inputs', () => {
+    const inputs = [
+      { address: 'not-a-hex-string', chainId: '0x1' },
+      {
+        address: '0x6982508145454Ce325dDbE47a25d4ec3d2311933',
+        chainId: 'not-a-hex-string',
+      },
+      { address: 'not-a-hex-string', chainId: 'not-a-hex-string' },
+    ];
+    inputs.forEach(({ address, chainId }) => {
+      const result = convertAddressToAssetCaipType(address, chainId);
+      expect(result).toBeUndefined();
+    });
+  });
+});
```

### ui/pages/asset/components/chart/asset-chart.tsx
```diff
@@ -1,4 +1,4 @@
-import React, { useEffect, useRef, useState } from 'react';
+import React, { useEffect, useMemo, useRef, useState } from 'react';
 import {
   Chart,
   LineElement,
@@ -14,7 +14,14 @@ import {
 import { Line } from 'react-chartjs-2';
 import classnames from 'classnames';
 import { brandColor } from '@metamask/design-tokens';
-import { CaipAssetType, Hex } from '@metamask/utils';
+import {
+  Hex,
+  isCaipAssetType,
+  isHexString,
+  KnownCaipNamespace,
+  toCaipAssetType,
+  hexToNumber,
+} from '@metamask/utils';
 import { trim } from 'lodash';
 import { Duration } from 'luxon';
 import { useTheme } from '../../../../hooks/useTheme';
@@ -132,6 +139,28 @@ const getTranslatedTimeRangeLabel = (
   );
 };
 
+export function convertAddressToAssetCaipType(
+  address: string,
+  chainId: string,
+) {
+  if (isCaipAssetType(address)) {
+    return address;
+  }
+
+  // Create EIP155 EVM asset type
+  if (isHexString(address) && isHexString(chainId)) {
+    return toCaipAssetType(
+      KnownCaipNamespace.Eip155,
+      hexToNumber(chainId).toString(),
+      'erc20',
+      address,
+    );
+  }
+
+  // Unsupported CAIP asset type
+  return undefined;
+}
+
 // A chart showing historic prices for a native or token asset
 const AssetChart = ({
   chainId,
@@ -149,7 +178,10 @@ const AssetChart = ({
   const t = useI18nContext();
   const theme = useTheme();
 
-  const timeRanges = useChartTimeRanges(address as CaipAssetType, currency);
+  const caipAssetType = useMemo(() => {
+    return convertAddressToAssetCaipType(address, chainId);
+  }, [address, chainId]);
+  const timeRanges = useChartTimeRanges(caipAssetType, currency);
 
   const [selectedTimeRange, setSelectedTimeRange] = useState<string>(
     timeRanges[0] ?? 'P1D',
```

### ui/pages/asset/hooks/useChartTimeRanges.test.ts
```diff
@@ -1,60 +1,54 @@
+import { CaipAssetType } from '@metamask/utils';
 import { renderHookWithProvider } from '../../../../test/lib/render-helpers';
 import { useChartTimeRanges } from './useChartTimeRanges';
 
 describe('useChartTimeRanges', () => {
-  describe('when the chain is EVM', () => {
-    it('returns hardcoded time ranges', () => {
-      const mockStateIsEvm = {
-        metamask: {
-          internalAccounts: {
-            accounts: {
-              '81b1ead4-334c-4921-9adf-282fde539752': {
-                id: '81b1ead4-334c-4921-9adf-282fde539752',
-                address: '0x458036e7bc0612e9b207640dc07ca7711346aae5',
-                type: 'eip155:eoa',
-              },
-            },
-            selectedAccount: '81b1ead4-334c-4921-9adf-282fde539752',
-          },
-          completedOnboarding: true,
-          historicalPrices: {},
-        },
-      };
-
+  describe('when the asset type is EVM', () => {
+    const mockState = {
+      metamask: {
+        historicalPrices: {},
+      },
+    };
+    const arrangeAct = (assetType?: CaipAssetType, currency?: string) => {
       const { result } = renderHookWithProvider(
-        () => useChartTimeRanges(),
-        mockStateIsEvm,
+        () => useChartTimeRanges(assetType, currency),
+        mockState,
       );
       const timeRanges = result.current;
+      return timeRanges;
+    };
+
+    it('returns hardcoded timeranges', () => {
+      const timeRanges = arrangeAct(
+        'eip155:1/erc20:0x6982508145454Ce325dDbE47a25d4ec3d2311933',
+        'USD',
+      );
+      expect(timeRanges).toEqual(['P1D', 'P1W', 'P1M', 'P3M', 'P1Y', 'P1000Y']);
+    });
 
+    it('returns hardcoded timestamps on missing asset type', () => {
+      jest.spyOn(console, 'warn').mockImplementation(jest.fn());
+      const timeRanges = arrangeAct(undefined, 'USD');
+      expect(timeRanges).toEqual(['P1D', 'P1W', 'P1M', 'P3M', 'P1Y', 'P1000Y']);
+    });
+
+    it('returns hardcoded timestamps on missing currency', () => {
+      jest.spyOn(console, 'warn').mockImplementation(jest.fn());
+      const timeRanges = arrangeAct(
+        'eip155:1/erc20:0x6982508145454Ce325dDbE47a25d4ec3d2311933',
+        undefined,
+      );
       expect(timeRanges).toEqual(['P1D', 'P1W', 'P1M', 'P3M', 'P1Y', 'P1000Y']);
     });
   });
 
   describe('when the chain is non-EVM', () => {
-    const mockStateNonEvm = {
-      metamask: {
-        internalAccounts: {
-          accounts: {
-            '5132883f-598e-482c-a02b-84eeaa352f5b': {
-              id: '5132883f-598e-482c-a02b-84eeaa352f5b',
-              address: '8A4AptCThfbuknsbteHgGKXczfJpfjuVA9SLTSGaaLGC',
-              type: 'solana:data-account',
-            },
-          },
-          selectedAccount: '5132883f-598e-482c-a02b-84eeaa352f5b',
-        },
-        completedOnboarding: true,
-      },
-    };
-
     it('returns time ranges available in historical prices', () => {
       const address = 'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/slip44:501';
       const currency = 'usd';
 
       const mockStateWithHistoricalPrices = {
         metamask: {
-          ...mockStateNonEvm.metamask,
           historicalPrices: {
             'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/slip44:501': {
               usd: {
@@ -83,7 +77,6 @@ describe('useChartTimeRanges', () => {
 
       const mockStateWithNoHistoricalPrices = {
         metamask: {
-          ...mockStateNonEvm.metamask,
           historicalPrices: {
             'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/slip44:501': {
               usd: {
@@ -109,7 +102,6 @@ describe('useChartTimeRanges', () => {
 
       const mockStateWithInvalidTimeRanges = {
         metamask: {
-          ...mockStateNonEvm.metamask,
           historicalPrices: {
             'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/slip44:501': {
               usd: {
@@ -139,7 +131,6 @@ describe('useChartTimeRanges', () => {
 
       const mockStateWithUnsortedTimeRanges = {
         metamask: {
-          ...mockStateNonEvm.metamask,
           historicalPrices: {
             'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp/slip44:501': {
               usd: {
```

### ui/pages/asset/hooks/useChartTimeRanges.ts
```diff
@@ -1,9 +1,13 @@
-import { CaipAssetType, assert } from '@metamask/utils';
+import {
+  CaipAssetType,
+  KnownCaipNamespace,
+  assert,
+  parseCaipAssetType,
+} from '@metamask/utils';
 import { chain } from 'lodash';
 import { Duration } from 'luxon';
 import { useSelector } from 'react-redux';
 import { getHistoricalPrices } from '../../../selectors/assets';
-import { getMultichainIsEvm } from '../../../selectors/multichain';
 
 /**
  * Returns the list of time ranges (as ISO 8601 durations) to display in the historical prices chart for a given asset.
@@ -20,17 +24,27 @@ export const useChartTimeRanges = (
   currency?: string,
 ): string[] => {
   const DEFAULT_TIME_RANGES = ['P1D', 'P1W', 'P1M', 'P3M', 'P1Y', 'P1000Y'];
-  const isEvm = useSelector(getMultichainIsEvm);
   const historicalPricesNonEvm = useSelector(getHistoricalPrices);
 
-  if (isEvm) {
-    // On EVM, time ranges are hardcoded
+  try {
+    assert(caipAssetType, 'caipAssetType is required on non-EVM chains');
+    assert(currency, 'currency is required on non-EVM chains');
+
+    if (
+      parseCaipAssetType(caipAssetType).chain.namespace ===
+      KnownCaipNamespace.Eip155
+    ) {
+      // On EVM, time ranges are hardcoded
+      return DEFAULT_TIME_RANGES;
+    }
+  } catch (e) {
+    console.warn(
+      'useChartTimeRanges - failed, returning default time ranges',
+      e,
+    );
     return DEFAULT_TIME_RANGES;
   }
 
-  assert(caipAssetType, 'caipAssetType is required on non-EVM chains');
-  assert(currency, 'currency is required on non-EVM chains');
-
   // On non-EVM, time ranges are the intervals defined in the the historicalPrices state
   const intervals =
     historicalPricesNonEvm[caipAssetType]?.[currency]?.intervals;
```
