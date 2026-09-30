# [?] fix: avoid double spend in sendAndConfirmTransaction

## Summary
Severity: Unknown
Chain: Solana
Component: solana-foundation/solana-web3.js
Published: 2020-06-15
Source: https://github.com/solana-foundation/solana-web3.js/commit/1f7d9a98b82f036a80021d3c6d40948f42d60a3b
Type: security-commit

## Details
fix: avoid double spend in sendAndConfirmTransaction

## Patch
### src/connection.js
```diff
@@ -10,7 +10,7 @@ import {Client as RpcWebSocketClient} from 'rpc-websockets';
 
 import {NonceAccount} from './nonce-account';
 import {PublicKey} from './publickey';
-import {DEFAULT_TICKS_PER_SLOT, NUM_TICKS_PER_SECOND} from './timing';
+import {MS_PER_SLOT} from './timing';
 import {Transaction} from './transaction';
 import {Message} from './message';
 import {sleep} from './util/sleep';
@@ -1285,19 +1285,14 @@ export class Connection {
     signature: TransactionSignature,
     confirmations: ?number,
   ): Promise<RpcResponseAndContext<SignatureStatus | null>> {
-    const NUM_STATUS_RETRIES = 10;
+    const start = Date.now();
+    const WAIT_TIMEOUT_MS = 60 * 1000;
 
-    const MS_PER_SECOND = 1000;
-    const MS_PER_SLOT =
-      (DEFAULT_TICKS_PER_SLOT / NUM_TICKS_PER_SECOND) * MS_PER_SECOND;
-
-    let statusRetries = NUM_STATUS_RETRIES;
     let statusResponse = await this.getSignatureStatus(signature);
     for (;;) {
       const status = statusResponse.value;
       if (status) {
         // Received a status, if not an error wait for confirmation
-        statusRetries = NUM_STATUS_RETRIES;
         if (
           status.err ||
           status.confirmations === null ||
@@ -1306,12 +1301,12 @@ export class Connection {
         ) {
           break;
         }
-      } else if (--statusRetries <= 0) {
+      } else if (Date.now() - start >= WAIT_TIMEOUT_MS) {
         break;
       }
 
-      // Sleep for approximately half a slot
-      await sleep(MS_PER_SLOT / 2);
+      // Sleep for approximately one slot
+      await sleep(MS_PER_SLOT);
       statusResponse = await this.getSignatureStatus(signature);
     }
 
@@ -1780,7 +1775,7 @@ export class Connection {
           }
 
           // Sleep for approximately half a slot
-          await sleep((500 * DEFAULT_TICKS_PER_SLOT) / NUM_TICKS_PER_SECOND);
+          await sleep(MS_PER_SLOT / 2);
 
           ++attempts;
         }
```

### src/timing.js
```diff
@@ -6,9 +6,20 @@
 /**
  * @ignore
  */
-export const NUM_TICKS_PER_SECOND = 10;
+export const NUM_TICKS_PER_SECOND = 160;
 
 /**
  * @ignore
  */
-export const DEFAULT_TICKS_PER_SLOT = 8;
+export const DEFAULT_TICKS_PER_SLOT = 64;
+
+/**
+ * @ignore
+ */
+export const NUM_SLOTS_PER_SECOND =
+  NUM_TICKS_PER_SECOND / DEFAULT_TICKS_PER_SLOT;
+
+/**
+ * @ignore
+ */
+export const MS_PER_SLOT = 1000 / NUM_SLOTS_PER_SECOND;
```

### src/transaction.js
```diff
@@ -210,7 +210,9 @@ export class Transaction {
     let numReadonlySignedAccounts = 0;
     let numReadonlyUnsignedAccounts = 0;
 
-    const accountKeys = this.signatures.map(({publicKey}) => publicKey.toString());
+    const accountKeys = this.signatures.map(({publicKey}) =>
+      publicKey.toString(),
+    );
     const programIds: string[] = [];
     const accountMetas: AccountMeta[] = [];
     this.instructions.forEach(instruction => {
```

### src/util/send-and-confirm-raw-transaction.js
```diff
@@ -6,6 +6,13 @@ import type {ConfirmOptions} from '../connection';
 
 /**
  * Send and confirm a raw transaction
+ *
+ * If `confirmations` count is not specified, wait for transaction to be finalized.
+ *
+ * @param {Connection} connection
+ * @param {Buffer} rawTransaction
+ * @param {ConfirmOptions} [options]
+ * @returns {Promise<TransactionSignature>}
  */
 export async function sendAndConfirmRawTransaction(
   connection: Connection,
```

### src/util/send-and-confirm-transaction.js
```diff
@@ -2,17 +2,20 @@
 
 import {Connection} from '../connection';
 import {Transaction} from '../transaction';
-import {sleep} from './sleep';
 import type {Account} from '../account';
 import type {ConfirmOptions} from '../connection';
 import type {TransactionSignature} from '../transaction';
 
-const NUM_SEND_RETRIES = 10;
-
 /**
  * Sign, send and confirm a transaction.
  *
  * If `confirmations` count is not specified, wait for transaction to be finalized.
+ *
+ * @param {Connection} connection
+ * @param {Transaction} transaction
+ * @param {Array<Account>} signers
+ * @param {ConfirmOptions} [options]
+ * @returns {Promise<TransactionSignature>}
  */
 export async function sendAndConfirmTransaction(
   connection: Connection,
@@ -21,34 +24,25 @@ export async function sendAndConfirmTransaction(
   options?: ConfirmOptions,
 ): Promise<TransactionSignature> {
   const start = Date.now();
-  let sendRetries = NUM_SEND_RETRIES;
-
-  for (;;) {
-    const signature = await connection.sendTransaction(
-      transaction,
-      signers,
-      options,
-    );
-    const status = (
-      await connection.confirmTransaction(
-        signature,
-        options && options.confirmations,
-      )
-    ).value;
-
-    if (status) {
-      if (status.err) {
-        throw new Error(
-          `Transaction ${signature} failed (${JSON.stringify(status)})`,
-        );
-      }
-      return signature;
+  const signature = await connection.sendTransaction(
+    transaction,
+    signers,
+    options,
+  );
+  const status = (
+    await connection.confirmTransaction(
+      signature,
+      options && options.confirmations,
+    )
+  ).value;
+
+  if (status) {
+    if (status.err) {
+      throw new Error(
+        `Transaction ${signature} failed (${JSON.stringify(status)})`,
+      );
     }
-
-    if (--sendRetries <= 0) break;
-
-    // Retry in 0..100ms to try to avoid another AccountInUse collision
-    await sleep(Math.random() * 100);
+    return signature;
   }
 
   const duration = (Date.now() - start) / 1000;
```
