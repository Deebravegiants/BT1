# [?] fix(wallet): polish modal overflow for manage accounts (#2827)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-09-26
Source: https://github.com/iotaledger/iota/commit/6690f13a86b35787a87934fe97fcf6a41df4c306
Type: security-commit

## Details
fix(wallet): polish modal overflow for manage accounts (#2827)

* fix(wallet): 3 dots menu on manage account. Use portal.

Signed-off-by: Eugene Panteleymonchuk <panteleymonchuk@gmail.com>

* fix(wallet): 3 dots menu on manage account. Fix position.

Signed-off-by: Eugene Panteleymonchuk <panteleymonchuk@gmail.com>

* feat(wallet): change position of popup, remove extra wrapper. Manage account page.

Signed-off-by: Eugene Panteleymonchuk <panteleymonchuk@gmail.com>

---------

Signed-off-by: Eugene Panteleymonchuk <panteleymonchuk@gmail.com>
Co-authored-by: Bran <52735957+brancoder@users.noreply.github.com>

## Patch
### apps/wallet/src/ui/app/pages/accounts/manage/AccountGroup.tsx
```diff
@@ -39,10 +39,14 @@ export function AccountGroup({
     accounts,
     type,
     accountSourceID,
+    isLast,
+    outerRef,
 }: {
     accounts: SerializedUIAccount[];
     type: AccountType;
     accountSourceID?: string;
+    isLast: boolean;
+    outerRef?: React.RefObject<HTMLDivElement>;
 }) {
     const [isDropdownOpen, setDropdownOpen] = useState(false);
     const navigate = useNavigate();
@@ -145,15 +149,19 @@ export function AccountGroup({
             >
                 {accounts.map((account, index) => (
                     <AccountGroupItem
+                        outerRef={outerRef}
                         isActive={activeAccount?.address === account.address}
                         key={account.id}
                         account={account}
-                        isLast={index === accounts.length - 1}
+                        showDropdownOptionsBottom={
+                            isLast &&
+                            (index === accounts.length - 1 || index === accounts.length - 2)
+                        }
                     />
                 ))}
             </Collapsible>
             <div
-                className={`absolute right-0 top-0 z-[100] bg-white ${isDropdownOpen ? '' : 'hidden'}`}
+                className={`absolute right-3 top-3 z-[100] bg-white ${isDropdownOpen ? '' : 'hidden'}`}
             >
                 <OutsideClickHandler onOutsideClick={() => setDropdownOpen(false)}>
                     <Dropdown>
```

### apps/wallet/src/ui/app/pages/accounts/manage/AccountGroupItem.tsx
```diff
@@ -2,7 +2,7 @@
 // SPDX-License-Identifier: Apache-2.0
 
 import { AccountType, type SerializedUIAccount } from '_src/background/accounts/Account';
-import { useState } from 'react';
+import { useState, useRef } from 'react';
 import clsx from 'clsx';
 import { formatAddress } from '@iota/iota-sdk/utils';
 import { ExplorerLinkType, NicknameDialog, useUnlockAccount } from '_components';
@@ -16,15 +16,26 @@ import { IotaLogoMark, Ledger } from '@iota/ui-icons';
 import { RemoveDialog } from './RemoveDialog';
 import { useBackgroundClient } from '_app/hooks/useBackgroundClient';
 import { isMainAccount } from '_src/background/accounts/isMainAccount';
+import { Portal } from '_app/shared/Portal';
 
 interface AccountGroupItemProps {
     account: SerializedUIAccount;
-    isLast: boolean;
+    showDropdownOptionsBottom: boolean;
     isActive?: boolean;
+    outerRef?: React.RefObject<HTMLDivElement>;
 }
 
-export function AccountGroupItem({ account, isLast, isActive }: AccountGroupItemProps) {
+export function AccountGroupItem({
+    account,
+    showDropdownOptionsBottom,
+    isActive,
+    outerRef,
+}: AccountGroupItemProps) {
     const [isDropdownOpen, setDropdownOpen] = useState(false);
+    const [dropdownPosition, setDropdownPosition] = useState({
+        y: 0,
+    });
+    const anchorRef = useRef<HTMLDivElement>(null);
     const [isDialogNicknameOpen, setDialogNicknameOpen] = useState(false);
     const [isDialogRemoveOpen, setDialogRemoveOpen] = useState(false);
     const accountName = account?.nickname ?? formatAddress(account?.address || '');
@@ -81,7 +92,24 @@ export function AccountGroupItem({ account, isLast, isActive }: AccountGroupItem
     }
 
     function handleOptionsClick(e: React.MouseEvent<HTMLButtonElement>) {
+        const outerTop = outerRef?.current?.getBoundingClientRect().top;
+        const innerTop = anchorRef?.current?.getBoundingClientRect().top;
+        const innerHeight = anchorRef?.current?.getBoundingClientRect().height;
         e.stopPropagation();
+
+        let y = 0;
+
+        if (innerTop && outerTop) {
+            y = innerTop - outerTop;
+        }
+
+        if (showDropdownOptionsBottom && innerHeight) {
+            y = y + innerHeight;
+        }
+
+        setDropdownPosition({
+            y: y,
+        });
         setDropdownOpen(true);
     }
 
@@ -99,7 +127,7 @@ export function AccountGroupItem({ account, isLast, isActive }: AccountGroupItem
 
     return (
         <div className="relative overflow-visible [&_span]:whitespace-nowrap">
-            <div onClick={handleSelectAccount}>
+            <div onClick={handleSelectAccount} ref={anchorRef}>
                 <Account
                     isLocked={account.isLocked}
                     isCopyable
@@ -118,31 +146,37 @@ export function AccountGroupItem({ account, isLast, isActive }: AccountGroupItem
                     onUnlockAccountClick={handleToggleLock}
                 />
             </div>
-            <div
-                className={clsx(
-                    `absolute right-0 z-[100] bg-white`,
-                    isLast ? 'bottom-0' : 'top-0',
-                    isDropdownOpen ? '' : 'hidden',
-                )}
-            >
-                <OutsideClickHandler onOutsideClick={() => setDropdownOpen(false)}>
-                    <Dropdown>
-                        <ListItem hideBottomBorder onClick={handleRename}>
-                            Rename
-                        </ListItem>
-                        {account.isKeyPairExportable ? (
-                            <ListItem hideBottomBorder onClick={handleExportPrivateKey}>
-                                Export Private Key
-                            </ListItem>
-                        ) : null}
-                        {allAccounts.isPending ? null : (
-                            <ListItem hideBottomBorder onClick={handleRemove}>
-                                Delete
-                            </ListItem>
+            <Portal containerId={'manage-account-item-portal-container'}>
+                {isDropdownOpen && (
+                    <div
+                        style={{
+                            top: dropdownPosition.y,
+                        }}
+                        className={clsx(
+                            `absolute right-0 z-[99] rounded-lg bg-white`,
+                            showDropdownOptionsBottom ? '-translate-y-full' : '',
                         )}
-                    </Dropdown>
-                </OutsideClickHandler>
-            </div>
+                    >
+                        <OutsideClickHandler onOutsideClick={() => setDropdownOpen(false)}>
+                            <Dropdown>
+                                <ListItem hideBottomBorder onClick={handleRename}>
+                                    Rename
+                                </ListItem>
+                                {account.isKeyPairExportable ? (
+                                    <ListItem hideBottomBorder onClick={handleExportPrivateKey}>
+                                        Export Private Key
+                                    </ListItem>
+                                ) : null}
+                                {allAccounts.isPending ? null : (
+                                    <ListItem hideBottomBorder onClick={handleRemove}>
+                                        Delete
+                                    </ListItem>
+                                )}
+                            </Dropdown>
+                        </OutsideClickHandler>
+                    </div>
+                )}
+            </Portal>
             <NicknameDialog
                 isOpen={isDialogNicknameOpen}
                 setOpen={setDialogNicknameOpen}
```

### apps/wallet/src/ui/app/pages/accounts/manage/ManageAccountsPage.tsx
```diff
@@ -1,6 +1,7 @@
 // Copyright (c) Mysten Labs, Inc.
 // Modifications Copyright (c) 2024 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
+import { useRef } from 'react';
 import { Button, ButtonType } from '@iota/apps-ui-kit';
 import { type AccountType } from '_src/background/accounts/Account';
 import { useInitializedGuard } from '_src/ui/app/hooks';
@@ -13,6 +14,7 @@ import { AccountGroup } from './AccountGroup';
 export function ManageAccountsPage() {
     const navigate = useNavigate();
     const groupedAccounts = useAccountGroups();
+    const outerRef = useRef<HTMLDivElement>(null);
     useInitializedGuard(true);
 
     function handleAdd() {
@@ -28,18 +30,23 @@ export function ManageAccountsPage() {
         >
             <div className="flex h-full w-full flex-col">
                 <div className="flex flex-1 flex-col overflow-y-auto">
-                    {Object.entries(groupedAccounts).map(([type, accountGroups]) =>
-                        Object.entries(accountGroups).map(([key, accounts]) => {
-                            return (
-                                <AccountGroup
-                                    key={`${type}-${key}`}
-                                    accounts={accounts}
-                                    accountSourceID={key}
-                                    type={type as AccountType}
-                                />
-                            );
-                        }),
-                    )}
+                    <div ref={outerRef} className="relative">
+                        {Object.entries(groupedAccounts).map(([type, accountGroups]) =>
+                            Object.entries(accountGroups).map(([key, accounts], index) => {
+                                return (
+                                    <AccountGroup
+                                        outerRef={outerRef}
+                                        key={`${type}-${key}`}
+                                        accounts={accounts}
+                                        accountSourceID={key}
+                                        type={type as AccountType}
+                                        isLast={index === Object.entries(accountGroups).length - 1}
+                                    />
+                                );
+                            }),
+                        )}
+                        <div id="manage-account-item-portal-container"></div>
+                    </div>
                 </div>
                 <div className="pt-sm">
                     <Button
```
