# [?] fix: delete all addresses will make dashboard page crashed

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2021-06-18
Source: https://github.com/RabbyHub/Rabby/commit/6298b4699ae12c2e9b30ef852970533b58ff3735
Type: security-commit

## Details
fix: delete all addresses will make dashboard page crashed

## Patch
### src/background/controller/wallet.ts
```diff
@@ -210,6 +210,8 @@ export class WalletController extends BaseController {
     const [account] = await this.getAccounts();
     if (account) {
       preferenceService.setCurrentAccount(account);
+    } else {
+      preferenceService.setCurrentAccount(null);
     }
   };
 
```

### src/background/service/preference.ts
```diff
@@ -10,7 +10,7 @@ export interface Account {
 }
 
 interface PreferenceStore {
-  currentAccount: Account | undefined;
+  currentAccount: Account | undefined | null;
   popupOpen: boolean;
   externalLinkAck: boolean;
   hiddenAddresses: Account[];
@@ -77,9 +77,11 @@ class PreferenceService {
     return cloneDeep(this.store.currentAccount);
   };
 
-  setCurrentAccount = (account: Account) => {
+  setCurrentAccount = (account: Account | null) => {
     this.store.currentAccount = account;
-    sessionService.broadcastEvent('accountsChanged', [account.address]);
+    if (account) {
+      sessionService.broadcastEvent('accountsChanged', [account.address]);
+    }
   };
 
   setPopupOpen = (isOpen) => {
```

### src/ui/views/Dashboard/index.tsx
```diff
@@ -1,7 +1,6 @@
 import React from 'react';
 import ClipboardJS from 'clipboard';
 import QRCode from 'qrcode.react';
-import { browser } from 'webextension-polyfill-ts';
 import { useEffect, useState } from 'react';
 import { Link, useHistory } from 'react-router-dom';
 import { message } from 'antd';
@@ -111,8 +110,12 @@ const Dashboard = () => {
     setPendingTxCount(total_count);
   };
 
+  if (!currentAccount) {
+    history.replace('/no-address');
+    return <></>;
+  }
+
   useEffect(() => {
-    if (!currentAccount) return;
     getPendingTxCount(currentAccount.address);
   }, [currentAccount]);
 
```
