# [?] fix: race condition in rpc websocket subscriptions

## Summary
Severity: Unknown
Chain: Solana
Component: solana-foundation/solana-web3.js
Published: 2020-02-10
Source: https://github.com/solana-foundation/solana-web3.js/commit/d6996835b69a9a69d4637cf23331b1dc860c4ea1
Type: security-commit

## Details
fix: race condition in rpc websocket subscriptions

## Patch
### src/connection.js
```diff
@@ -566,13 +566,18 @@ type KeyedAccountInfo = {
  */
 export type AccountChangeCallback = (accountInfo: AccountInfo) => void;
 
+/**
+ * @private
+ */
+type SubscriptionId = 'subscribing' | number;
+
 /**
  * @private
  */
 type AccountSubscriptionInfo = {
   publicKey: string, // PublicKey of the account as a base 58 string
   callback: AccountChangeCallback,
-  subscriptionId: null | number, // null when there's no current server subscription id
+  subscriptionId: ?SubscriptionId, // null when there's no current server subscription id
 };
 
 /**
@@ -588,7 +593,7 @@ export type ProgramAccountChangeCallback = (
 type ProgramAccountSubscriptionInfo = {
   programId: string, // PublicKey of the program as a base 58 string
   callback: ProgramAccountChangeCallback,
-  subscriptionId: null | number, // null when there's no current server subscription id
+  subscriptionId: ?SubscriptionId, // null when there's no current server subscription id
 };
 
 /**
@@ -601,7 +606,7 @@ export type SlotChangeCallback = (slotInfo: SlotInfo) => void;
  */
 type SlotSubscriptionInfo = {
   callback: SlotChangeCallback,
-  subscriptionId: null | number, // null when there's no current server subscription id
+  subscriptionId: ?SubscriptionId, // null when there's no current server subscription id
 };
 
 /**
@@ -617,7 +622,7 @@ export type SignatureResultCallback = (
 type SignatureSubscriptionInfo = {
   signature: TransactionSignature, // TransactionSignature as a base 58 string
   callback: SignatureResultCallback,
-  subscriptionId: null | number, // null when there's no current server subscription id
+  subscriptionId: ?SubscriptionId, // null when there's no current server subscription id
 };
 
 /**
@@ -1315,6 +1320,50 @@ export class Connection {
     }
   }
 
+  /**
+   * @private
+   */
+  async _subscribe<SubInfo: {subscriptionId: ?SubscriptionId}, RpcArgs>(
+    sub: SubInfo,
+    rpcMethod: string,
+    rpcArgs: RpcArgs,
+  ) {
+    if (sub.subscriptionId == null) {
+      sub.subscriptionId = 'subscribing';
+      try {
+        const id = await this._rpcWebSocket.call(rpcMethod, rpcArgs);
+        if (sub.subscriptionId === 'subscribing') {
+          // eslint-disable-next-line require-atomic-updates
+          sub.subscriptionId = id;
+        }
+      } catch (err) {
+        if (sub.subscriptionId === 'subscribing') {
+          // eslint-disable-next-line require-atomic-updates
+          sub.subscriptionId = null;
+        }
+        console.error(`${rpcMethod} error for argument`, rpcArgs, err.message);
+      }
+    }
+  }
+
+  /**
+   * @private
+   */
+  async _unsubscribe<SubInfo: {subscriptionId: ?SubscriptionId}>(
+    sub: SubInfo,
+    rpcMethod: string,
+  ) {
+    const subscriptionId = sub.subscriptionId;
+    if (subscriptionId != null && typeof subscriptionId != 'string') {
+      const unsubscribeId: number = subscriptionId;
+      try {
+        await this._rpcWebSocket.call(rpcMethod, [unsubscribeId]);
+      } catch (err) {
+        console.log(`${rpcMethod} error:`, err.message);
+      }
+    }
+  }
+
   /**
    * @private
    */
@@ -1355,66 +1404,23 @@ export class Connection {
     }
 
     for (let id of accountKeys) {
-      const {subscriptionId, publicKey} = this._accountChangeSubscriptions[id];
-      if (subscriptionId === null) {
-        try {
-          this._accountChangeSubscriptions[
-            id
-          ].subscriptionId = await this._rpcWebSocket.call('accountSubscribe', [
-            publicKey,
-          ]);
-        } catch (err) {
-          console.log(
-            `accountSubscribe error for ${publicKey}: ${err.message}`,
-          );
-        }
-      }
+      const sub: AccountSubscriptionInfo = this._accountChangeSubscriptions[id];
+      await this._subscribe(sub, 'accountSubscribe', [sub.publicKey]);
     }
+
     for (let id of programKeys) {
-      const {
-        subscriptionId,
-        programId,
-      } = this._programAccountChangeSubscriptions[id];
-      if (subscriptionId === null) {
-        try {
-          this._programAccountChangeSubscriptions[
-            id
-          ].subscriptionId = await this._rpcWebSocket.call('programSubscribe', [
-            programId,
-          ]);
-        } catch (err) {
-          console.log(
-            `programSubscribe error for ${programId}: ${err.message}`,
-          );
-        }
-      }
+      const sub = this._programAccountChangeSubscriptions[id];
+      await this._subscribe(sub, 'programSubscribe', [sub.programId]);
     }
+
     for (let id of slotKeys) {
-      const {subscriptionId} = this._slotSubscriptions[id];
-      if (subscriptionId === null) {
-        try {
-          this._slotSubscriptions[
-            id
-          ].subscriptionId = await this._rpcWebSocket.call('slotSubscribe', []);
-        } catch (err) {
-          console.log(`slotSubscribe error: ${err.message}`);
-        }
-      }
+      const sub = this._slotSubscriptions[id];
+      await this._subscribe(sub, 'slotSubscribe', []);
     }
+
     for (let id of signatureKeys) {
-      const subscription = this._signatureSubscriptions[id];
-      if (subscription.subscriptionId === null) {
-        subscription.subscriptionId = -1; // indicates subscribing
-        try {
-          const id = await this._rpcWebSocket.call('signatureSubscribe', [
-            subscription.signature,
-          ]);
-          subscription.subscriptionId = id;
-        } catch (err) {
-          subscription.subscriptionId = null;
-          console.log(`signatureSubscribe error: ${err.message}`);
-        }
-      }
+      const sub = this._signatureSubscriptions[id];
+      await this._subscribe(sub, 'signatureSubscribe', [sub.signature]);
     }
   }
 
@@ -1473,15 +1479,9 @@ export class Connection {
    */
   async removeAccountChangeListener(id: number): Promise<void> {
     if (this._accountChangeSubscriptions[id]) {
-      const {subscriptionId} = this._accountChangeSubscriptions[id];
+      const subInfo = this._accountChangeSubscriptions[id];
       delete this._accountChangeSubscriptions[id];
-      if (subscriptionId !== null) {
-        try {
-          await this._rpcWebSocket.call('accountUnsubscribe', [subscriptionId]);
-        } catch (err) {
-          console.log('accountUnsubscribe error:', err.message);
-        }
-      }
+      await this._unsubscribe(subInfo, 'accountUnsubscribe');
       this._updateSubscriptions();
     } else {
       throw new Error(`Unknown account change id: ${id}`);
@@ -1549,18 +1549,12 @@ export class Connection {
    */
   async removeProgramAccountChangeListener(id: number): Promise<void> {
     if (this._programAccountChangeSubscriptions[id]) {
-      const {subscriptionId} = this._programAccountChangeSubscriptions[id];
+      const subInfo = this._programAccountChangeSubscriptions[id];
       delete this._programAccountChangeSubscriptions[id];
-      if (subscriptionId !== null) {
-        try {
-          await this._rpcWebSocket.call('programUnsubscribe', [subscriptionId]);
-        } catch (err) {
-          console.log('programUnsubscribe error:', err.message);
-        }
-      }
+      await this._unsubscribe(subInfo, 'programUnsubscribe');
       this._updateSubscriptions();
     } else {
-      throw new Error(`Unknown account change id: ${id}`);
+      throw new Error(`Unknown program account change id: ${id}`);
     }
   }
 
@@ -1612,15 +1606,9 @@ export class Connection {
    */
   async removeSlotChangeListener(id: number): Promise<void> {
     if (this._slotSubscriptions[id]) {
-      const {subscriptionId} = this._slotSubscriptions[id];
+      const subInfo = this._slotSubscriptions[id];
       delete this._slotSubscriptions[id];
-      if (subscriptionId !== null) {
-        try {
-          await this._rpcWebSocket.call('slotUnsubscribe', [subscriptionId]);
-        } catch (err) {
-          console.log('slotUnsubscribe error:', err.message);
-        }
-      }
+      await this._unsubscribe(subInfo, 'slotUnsubscribe');
       this._updateSubscriptions();
     } else {
       throw new Error(`Unknown slot change id: ${id}`);
@@ -1662,6 +1650,7 @@ export class Connection {
   /**
    * Register a callback to be invoked upon signature updates
    *
+   * @param signature Transaction signature string in base 58
    * @param callback Function to invoke on signature notifications
    * @return subscription id
    */
@@ -1686,20 +1675,12 @@ export class Connection {
    */
   async removeSignatureListener(id: number): Promise<void> {
     if (this._signatureSubscriptions[id]) {
-      const {subscriptionId} = this._signatureSubscriptions[id];
+      const subInfo = this._signatureSubscriptions[id];
       delete this._signatureSubscriptions[id];
-      if (subscriptionId !== null) {
-        try {
-          await this._rpcWebSocket.call('signatureUnsubscribe', [
-            subscriptionId,
-          ]);
-        } catch (err) {
-          console.log('signatureUnsubscribe error:', err.message);
-        }
-      }
+      await this._unsubscribe(subInfo, 'signatureUnsubscribe');
       this._updateSubscriptions();
     } else {
-      throw new Error(`Unknown signature change id: ${id}`);
+      throw new Error(`Unknown signature result id: ${id}`);
     }
   }
 }
```
