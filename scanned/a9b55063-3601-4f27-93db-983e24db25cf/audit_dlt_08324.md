# [?] fix: race condition in rpc unsubscribe

## Summary
Severity: Unknown
Chain: Solana
Component: solana-foundation/solana-web3.js
Published: 2020-02-11
Source: https://github.com/solana-foundation/solana-web3.js/commit/7fabc9e348354d5e0219dfe7c0fe44896290fc9f
Type: security-commit

## Details
fix: race condition in rpc unsubscribe

## Patch
### src/connection.js
```diff
@@ -1367,7 +1367,7 @@ export class Connection {
   /**
    * @private
    */
-  async _updateSubscriptions() {
+  _updateSubscriptions() {
     const accountKeys = Object.keys(this._accountChangeSubscriptions).map(
       Number,
     );
@@ -1404,23 +1404,23 @@ export class Connection {
     }
 
     for (let id of accountKeys) {
-      const sub: AccountSubscriptionInfo = this._accountChangeSubscriptions[id];
-      await this._subscribe(sub, 'accountSubscribe', [sub.publicKey]);
+      const sub = this._accountChangeSubscriptions[id];
+      this._subscribe(sub, 'accountSubscribe', [sub.publicKey]);
     }
 
     for (let id of programKeys) {
       const sub = this._programAccountChangeSubscriptions[id];
-      await this._subscribe(sub, 'programSubscribe', [sub.programId]);
+      this._subscribe(sub, 'programSubscribe', [sub.programId]);
     }
 
     for (let id of slotKeys) {
       const sub = this._slotSubscriptions[id];
-      await this._subscribe(sub, 'slotSubscribe', []);
+      this._subscribe(sub, 'slotSubscribe', []);
     }
 
     for (let id of signatureKeys) {
       const sub = this._signatureSubscriptions[id];
-      await this._subscribe(sub, 'signatureSubscribe', [sub.signature]);
+      this._subscribe(sub, 'signatureSubscribe', [sub.signature]);
     }
   }
 
```
