# [?] fix(explorer): overflows and tx summary (#3037)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-10-07
Source: https://github.com/iotaledger/iota/commit/dedb0ea699c8e351df87cd60a1ca3408487dee8b
Type: security-commit

## Details
fix(explorer): overflows and tx summary (#3037)

## Patch
### apps/explorer/src/components/object/ObjectFieldsCard.tsx
```diff
@@ -158,6 +158,7 @@ export function ObjectFieldsCard({
                                             keyText={name}
                                             value={getFieldTypeValue(type, objectType).displayName}
                                             isTruncated
+                                            fullwidth
                                         />
                                     </ButtonUnstyled>
                                 ))}
```

### apps/explorer/src/hooks/useBreakpoint.ts
```diff
@@ -8,11 +8,10 @@ import { useMediaQuery } from '~/hooks/useMediaQuery';
  * values taken from tailwind.config.js
  */
 export const BREAK_POINT = {
-    sm: 640,
-    md: 768,
-    lg: 1024,
-    xl: 1280,
-    '2xl': 1536,
+    sm: 768,
+    md: 1024,
+    lg: 1400,
+    xl: 1920,
 };
 
 export function useBreakpoint(breakpoint: keyof typeof BREAK_POINT): boolean {
```

### apps/explorer/src/pages/transaction-result/TransactionView.tsx
```diff
@@ -57,7 +57,7 @@ export function TransactionView({ transaction }: TransactionViewProps): JSX.Elem
                     />
                 </div>
                 <div className="flex flex-col gap-md md:flex-row">
-                    <div className="flex h-full w-full flex-1 md:h-full md:max-h-screen md:w-1/3">
+                    <div className="flex h-full w-full flex-1 overflow-auto md:h-full md:max-h-screen md:w-1/3">
                         <div className="w-full">
                             <Panel>
                                 <SegmentedButton type={SegmentedButtonType.Transparent}>
```

### apps/explorer/src/pages/transaction-result/transaction-summary/BalanceChanges.tsx
```diff
@@ -24,14 +24,19 @@ import clsx from 'clsx';
 import { useMemo } from 'react';
 import { CoinIcon } from '~/components';
 import { AddressLink, CollapsibleCard, CollapsibleSection } from '~/components/ui';
+import { BREAK_POINT, useMediaQuery } from '~/hooks';
 
 interface BalanceChangesProps {
     changes: BalanceChangeSummary;
 }
 
 function BalanceChangeEntry({ change }: { change: BalanceChange }): JSX.Element | null {
     const { amount, coinType, recipient, unRecognizedToken } = change;
-    const [formatted, symbol] = useFormatCoin(amount, coinType, CoinFormat.FULL);
+    const isMdScreen = useMediaQuery(
+        `(min-width: ${BREAK_POINT.md}px) and (max-width: ${BREAK_POINT.lg - 1}px)`,
+    );
+    const coinFormat = isMdScreen ? CoinFormat.ROUNDED : CoinFormat.FULL;
+    const [formatted, symbol] = useFormatCoin(amount, coinType, coinFormat);
     const { data: coinMetaData } = useCoinMetadata(coinType);
     const isPositive = BigInt(amount) > 0n;
 
```

### apps/explorer/src/pages/transaction-result/transaction-summary/ObjectChanges.tsx
```diff
@@ -95,7 +95,7 @@ function ObjectDetailPanel({ panelContent, headerContent }: ObjectDetailPanelPro
             hideArrow
             render={() => (
                 <div className="flex w-full flex-row items-center justify-between px-md--rs">
-                    <div className="flex flex-row gap-xxxs pl-xxs text-neutral-40 dark:text-neutral-60">
+                    <div className="flex flex-row gap-xxxs text-neutral-40 dark:text-neutral-60">
                         <span className="text-body-md">Object</span>
 
                         <TriangleDown
@@ -107,7 +107,9 @@ function ObjectDetailPanel({ panelContent, headerContent }: ObjectDetailPanelPro
                             )}
                         />
                     </div>
-                    <div className="flex flex-row items-center gap-xxs pr-xxs">{headerContent}</div>
+                    <div className="flex flex-row items-center gap-xxs truncate pr-xxs">
+                        {headerContent}
+                    </div>
                 </div>
             )}
             open={open}
```

### apps/explorer/src/pages/transaction-result/transaction-summary/index.tsx
```diff
@@ -28,7 +28,7 @@ export function TransactionSummary({ transaction }: TransactionSummaryProps): JS
     const upgradedSystemPackages = summary?.upgradedSystemPackages;
 
     return (
-        <div className="flex flex-wrap gap-lg px-md--rs py-md md:py-md">
+        <div className="flex flex-wrap gap-lg px-md--rs py-md md:py-sm">
             {balanceChanges && transactionKindName === 'ProgrammableTransaction' && (
                 <BalanceChanges changes={balanceChanges} />
             )}
```
