# [?] fix(wallet,wallet-dashboard): avoid overflows caused by long names (#8400)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-09-02
Source: https://github.com/iotaledger/iota/commit/d33ae837af532dee129c303e1d6e65994b3b7b67
Type: security-commit

## Details
fix(wallet,wallet-dashboard): avoid overflows caused by long names (#8400)

# Description of change

There are many places where there can be overflow if a user has a long
name as default. This PR aims to fix that.

## Links to any relevant issues


Fixes #8388 
Fixes #8356 

## How the change has been tested

- [ ] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes

---------

Co-authored-by: Juliana <115430927+Juligs@users.noreply.github.com>

## Patch
### apps/core/package.json
```diff
@@ -30,7 +30,7 @@
         "@iota/apps-ui-kit": "workspace:*",
         "@iota/dapp-kit": "workspace:*",
         "@iota/graphql-transport": "workspace:*",
-        "@iota/iota-names-sdk": "^0.1.1",
+        "@iota/iota-names-sdk": "^0.2.0",
         "@iota/iota-sdk": "workspace:*",
         "@iota/kiosk": "workspace:*",
         "@noble/hashes": "^1.4.0",
```

### apps/core/src/components/cards/BalanceChanges.tsx
```diff
@@ -9,7 +9,7 @@ import { ExplorerLinkType } from '../../enums';
 import { formatAddress, CoinFormat } from '@iota/iota-sdk/utils';
 import { CoinItem } from '../coin';
 import { RecognizedBadge } from '@iota/apps-ui-icons';
-import { getRecognizedUnRecognizedTokenChanges } from '../../utils';
+import { formatIotaName, getRecognizedUnRecognizedTokenChanges } from '../../utils';
 import { BalanceChange } from '../../interfaces';
 import { useGetDefaultIotaName } from '../../hooks';
 import { NamedAddressTooltip } from '../NamedAddressTooltip';
@@ -64,7 +64,7 @@ function BalanceChangePanel({
                         value={
                             <NamedAddressTooltip name={name} address={owner}>
                                 <ExplorerLink type={ExplorerLinkType.Address} address={owner}>
-                                    {name || formatAddress(owner)}
+                                    {formatIotaName(name) || formatAddress(owner)}
                                 </ExplorerLink>
                             </NamedAddressTooltip>
                         }
```

### apps/core/src/components/cards/ObjectChangeDisplay.tsx
```diff
@@ -31,7 +31,9 @@ export function ObjectChangeDisplay({
                         disableAutoPlay
                     />
                 </CardImage>
-                <CardBody title={name} subtitle={display.description ?? ''} />
+                <div className="truncate overflow-x-hidden [&_div]:truncate">
+                    <CardBody title={name} subtitle={display.description ?? ''} />
+                </div>
                 {objectId && <CardAction type={CardActionType.Link} icon={<ArrowTopRight />} />}
             </Card>
         </ExplorerLink>
```

### apps/core/src/components/cards/ObjectChanges.tsx
```diff
@@ -10,6 +10,7 @@ import {
     type IotaObjectChangeWithDisplay,
     ExplorerLinkType,
     useGetDefaultIotaName,
+    formatIotaName,
 } from '../../';
 import { formatAddress } from '@iota/iota-sdk/utils';
 import cx from 'clsx';
@@ -235,7 +236,7 @@ function ObjectChangeByOwnerPanel({
                             value={
                                 <NamedAddressTooltip name={iotaName} address={owner}>
                                     <ExplorerLink type={ExplorerLinkType.Address} address={owner}>
-                                        {iotaName || formatAddress(owner)}
+                                        {formatIotaName(iotaName) || formatAddress(owner)}
                                     </ExplorerLink>
                                 </NamedAddressTooltip>
                             }
```

### apps/core/src/utils/formatIotaName.ts
```diff
@@ -0,0 +1,13 @@
+// Copyright (c) 2025 IOTA Stiftung
+// SPDX-License-Identifier: Apache-2.0
+
+import { normalizeIotaName } from '@iota/iota-names-sdk';
+
+export function formatIotaName(name: string | null | undefined): string | null {
+    if (!name) return null;
+    return normalizeIotaName(name, 'at', {
+        onlyFirstSubname: true,
+        truncateLongParts: true,
+        ellipsisForDeepSubnames: true,
+    });
+}
```

### apps/core/src/utils/index.ts
```diff
@@ -29,6 +29,7 @@ export * from './extractMediaFileType';
 export * from './nftMediaUtils';
 export * from './mapTimelockObjects';
 export * from './formatDelegatedTimelockedStake';
+export * from './formatIotaName';
 
 export * from './stake';
 export * from './transaction';
```

### apps/explorer/package.json
```diff
@@ -29,7 +29,7 @@
         "@iota/apps-ui-kit": "workspace:*",
         "@iota/core": "workspace:*",
         "@iota/dapp-kit": "workspace:*",
-        "@iota/iota-names-sdk": "^0.1.1",
+        "@iota/iota-names-sdk": "^0.2.0",
         "@iota/iota-sdk": "workspace:*",
         "@sentry/react": "^7.120.3",
         "@tanstack/react-query": "^5.50.1",
```

### apps/wallet-dashboard/components/dialogs/ReceiveFundsDialog.tsx
```diff
@@ -38,15 +38,15 @@ export function ReceiveFundsDialog({
             <DialogContent containerId="overlay-portal-container">
                 <Header title="Receive" onClose={() => setOpen(false)} />
                 <DialogBody>
-                    <div className="flex flex-col gap-lg text-center [&_span]:w-full [&_span]:break-words">
+                    <div className="flex max-h-[500px] flex-col gap-lg overflow-y-auto text-center [&_span]:w-full [&_span]:break-words">
                         <div className="self-center">
                             <QR value={address} size={130} marginSize={2} />
                         </div>
 
                         <div className="flex flex-col gap-xs">
                             {iotaName && (
                                 <Panel bgColor="bg-iota-neutral-96 dark:bg-iota-neutral-12">
-                                    <div className="px-md--rs py-xs text-title-lg text-iota-neutral-12 dark:text-iota-neutral-96">
+                                    <div className="break-words px-md--rs py-xs text-title-lg text-iota-neutral-12 dark:text-iota-neutral-96">
                                         {iotaName}
                                     </div>
                                 </Panel>
```

### apps/wallet-dashboard/components/dialogs/assets/views/DetailsView.tsx
```diff
@@ -7,6 +7,9 @@ import {
     Collapsible,
     useNFTBasicData,
     NFTMediaDisplayCard,
+    useGetDefaultIotaName,
+    formatIotaName,
+    NamedAddressTooltip,
 } from '@iota/core';
 import { Button, ButtonType, Header, KeyValueInfo } from '@iota/apps-ui-kit';
 import { formatAddress } from '@iota/iota-sdk/utils';
@@ -40,6 +43,7 @@ export function DetailsView({ onClose, asset, onSend, onBack }: DetailsViewProps
         kioskItem,
         objectData,
     } = useNftDetails(objectId, senderAddress);
+    const { data: iotaName } = useGetDefaultIotaName(ownerAddress);
     const { fileExtensionType, filePath } = useNFTBasicData(objectData);
 
     function handleMoreAboutKiosk() {
@@ -76,11 +80,11 @@ export function DetailsView({ onClose, asset, onSend, onBack }: DetailsViewProps
                     </ExplorerLink>
                     <div className="flex w-full flex-col gap-md">
                         <div className="flex flex-col gap-xxxs">
-                            <span className="text-title-lg text-iota-neutral-10 dark:text-iota-neutral-92">
+                            <span className="break-words text-title-lg text-iota-neutral-10 dark:text-iota-neutral-92">
                                 {nftDisplayData?.name}
                             </span>
                             {nftDisplayData?.description ? (
-                                <span className="text-body-md text-iota-neutral-60">
+                                <span className="break-words text-body-md text-iota-neutral-60">
                                     {nftDisplayData?.description}
                                 </span>
                             ) : null}
@@ -111,12 +115,18 @@ export function DetailsView({ onClose, asset, onSend, onBack }: DetailsViewProps
                                     <KeyValueInfo
                                         keyText="Owner"
                                         value={
-                                            <ExplorerLink
-                                                type={ExplorerLinkType.Address}
+                                            <NamedAddressTooltip
+                                                name={iotaName}
                                                 address={ownerAddress}
                                             >
-                                                {formatAddress(ownerAddress)}
-                                            </ExplorerLink>
+                                                <ExplorerLink
+                                                    type={ExplorerLinkType.Address}
+                                                    address={ownerAddress}
+                                                >
+                                                    {formatIotaName(iotaName) ||
+                                                        formatAddress(ownerAddress)}
+                                                </ExplorerLink>
+                                            </NamedAddressTooltip>
                                         }
                                         fullwidth
                                     />
```

### apps/wallet-dashboard/components/dialogs/assets/views/SendView.tsx
```diff
@@ -55,7 +55,7 @@ export function SendView({ objectId, senderAddress, objectType, onClose, onBack
                         />
                     </div>
                     <div className="flex w-full flex-col gap-md">
-                        <div className="flex flex-col items-center gap-xxxs">
+                        <div className="flex flex-col items-center gap-xxxs break-words [&_div]:max-w-full [&_h4]:max-w-full [&_h4]:break-words">
                             <Title title={nftName} />
                         </div>
                         <AddressInput
```

### apps/wallet-dashboard/package.json
```diff
@@ -28,7 +28,7 @@
         "@iota/apps-ui-kit": "workspace:*",
         "@iota/core": "workspace:*",
         "@iota/dapp-kit": "workspace:*",
-        "@iota/iota-names-sdk": "^0.1.1",
+        "@iota/iota-names-sdk": "^0.2.0",
         "@iota/iota-sdk": "workspace:*",
         "@iota/wallet-standard": "workspace:*",
         "@sentry/nextjs": "^7.120.3",
```

### apps/wallet/package.json
```diff
@@ -95,7 +95,7 @@
         "@iota/apps-ui-kit": "workspace:*",
         "@iota/core": "workspace:*",
         "@iota/dapp-kit": "workspace:*",
-        "@iota/iota-names-sdk": "^0.1.1",
+        "@iota/iota-names-sdk": "^0.2.0",
         "@iota/iota-sdk": "workspace:*",
         "@iota/kiosk": "workspace:*",
         "@iota/ledgerjs-hw-app-iota": "workspace:*",
```
