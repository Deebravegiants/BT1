# [?] Push TX: Include validation to prevent DoS

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2023-04-20
Source: https://github.com/mempool/mempool/commit/21a47a7b4bdcbb00f50064b0cfab052ca53d3c2c
Type: security-commit

## Details
Push TX: Include validation to prevent DoS

## Patch
### backend/src/api/bitcoin/bitcoin.routes.ts
```diff
@@ -723,12 +723,7 @@ class BitcoinRoutes {
   private async $postTransaction(req: Request, res: Response) {
     res.setHeader('content-type', 'text/plain');
     try {
-      let rawTx;
-      if (typeof req.body === 'object') {
-        rawTx = Object.keys(req.body)[0];
-      } else {
-        rawTx = req.body;
-      }
+      const rawTx = Common.getTransactionFromRequest(req, false);
       const txIdResult = await bitcoinApi.$sendRawTransaction(rawTx);
       res.send(txIdResult);
     } catch (e: any) {
@@ -739,12 +734,8 @@ class BitcoinRoutes {
 
   private async $postTransactionForm(req: Request, res: Response) {
     res.setHeader('content-type', 'text/plain');
-    const matches = /tx=([a-z0-9]+)/.exec(req.body);
-    let txHex = '';
-    if (matches && matches[1]) {
-      txHex = matches[1];
-    }
     try {
+      const txHex = Common.getTransactionFromRequest(req, true);
       const txIdResult = await bitcoinClient.sendRawTransaction(txHex);
       res.send(txIdResult);
     } catch (e: any) {
```

### backend/src/api/common.ts
```diff
@@ -1,3 +1,5 @@
+import * as bitcoinjs from 'bitcoinjs-lib';
+import { Request } from 'express';
 import { Ancestor, CpfpInfo, CpfpSummary, CpfpCluster, EffectiveFeeStats, MempoolBlockWithTransactions, TransactionExtended, MempoolTransactionExtended, TransactionStripped, WorkingEffectiveFeeStats } from '../mempool.interfaces';
 import config from '../config';
 import { NodeSocket } from '../repositories/NodesSocketsRepository';
@@ -511,6 +513,89 @@ export class Common {
   static getNthPercentile(n: number, sortedDistribution: any[]): any {
     return sortedDistribution[Math.floor((sortedDistribution.length - 1) * (n / 100))];
   }
+
+  static getTransactionFromRequest(req: Request, form: boolean): string {
+    let rawTx: any = typeof req.body === 'object' && form
+      ? Object.values(req.body)[0] as any
+      : req.body;
+    if (typeof rawTx !== 'string') {
+      throw Object.assign(new Error('Non-string request body'), { code: -1 });
+    }
+
+    // Support both upper and lower case hex
+    // Support both txHash= Form and direct API POST
+    const reg = form ? /^txHash=((?:[a-fA-F0-9]{2})+)$/ : /^((?:[a-fA-F0-9]{2})+)$/;
+    const matches = reg.exec(rawTx);
+    if (!matches || !matches[1]) {
+      throw Object.assign(new Error('Non-hex request body'), { code: -2 });
+    }
+
+    // Guaranteed to be a hex string of multiple of 2
+    // Guaranteed to be lower case
+    // Guaranteed to pass validation (see function below)
+    return this.validateTransactionHex(matches[1].toLowerCase());
+  }
+
+  private static validateTransactionHex(txhex: string): string {
+    // Do not mutate txhex
+
+    // We assume txhex to be valid hex (output of getTransactionFromRequest above)
+
+    // Check 1: Valid transaction parse
+    let tx: bitcoinjs.Transaction;
+    try {
+      tx = bitcoinjs.Transaction.fromHex(txhex);
+    } catch(e) {
+      throw Object.assign(new Error('Invalid transaction (could not parse)'), { code: -4 });
+    }
+
+    // Check 2: Simple size check
+    if (tx.weight() > config.MEMPOOL.MAX_PUSH_TX_SIZE_WEIGHT) {
+      throw Object.assign(new Error(`Transaction too large (max ${config.MEMPOOL.MAX_PUSH_TX_SIZE_WEIGHT} weight units)`), { code: -3 });
+    }
+
+    // Check 3: Check unreachable script in taproot (if not allowed)
+    if (!config.MEMPOOL.ALLOW_UNREACHABLE) {
+      tx.ins.forEach(input => {
+        const witness = input.witness;
+        // See BIP 341: Script validation rules
+        const hasAnnex = witness.length >= 2 &&
+          witness[witness.length - 1].length > 1 &&
+          witness[witness.length - 1][0] === 0x50;
+        const scriptSpendMinLength = hasAnnex ? 3 : 2;
+        const maybeScriptSpend = witness.length >= scriptSpendMinLength;
+
+        if (maybeScriptSpend) {
+          const controlBlock = witness[witness.length - scriptSpendMinLength + 1];
+          if (controlBlock.length === 0 || (controlBlock[0] & 0xfe) < 0xc0) {
+            // Skip this input, it's not taproot
+            return;
+          }
+          // Definitely taproot. Get script
+          const script = witness[witness.length - scriptSpendMinLength];
+          const decompiled = bitcoinjs.script.decompile(script);
+          if (!decompiled || decompiled.length < 2) {
+            // Skip this input
+            return;
+          }
+          // Iterate up to second last (will look ahead 1 item)
+          for (let i = 0; i < decompiled.length - 1; i++) {
+            const first = decompiled[i];
+            const second = decompiled[i + 1];
+            if (
+              first === bitcoinjs.opcodes.OP_FALSE &&
+              second === bitcoinjs.opcodes.OP_IF
+            ) {
+              throw Object.assign(new Error('Unreachable taproot scripts not allowed'), { code: -5 });
+            }
+          }
+        }
+      })
+    }
+
+    // Pass through the input string untouched
+    return txhex;
+  }
 }
 
 /**
```

### backend/src/config.ts
```diff
@@ -35,6 +35,8 @@ interface IConfig {
     CPFP_INDEXING: boolean;
     MAX_BLOCKS_BULK_QUERY: number;
     DISK_CACHE_BLOCK_INTERVAL: number;
+    MAX_PUSH_TX_SIZE_WEIGHT: number;
+    ALLOW_UNREACHABLE: boolean;
   };
   ESPLORA: {
     REST_API_URL: string;
@@ -165,6 +167,8 @@ const defaults: IConfig = {
     'CPFP_INDEXING': false,
     'MAX_BLOCKS_BULK_QUERY': 0,
     'DISK_CACHE_BLOCK_INTERVAL': 6,
+    'MAX_PUSH_TX_SIZE_WEIGHT': 400000,
+    'ALLOW_UNREACHABLE': true,
   },
   'ESPLORA': {
     'REST_API_URL': 'http://127.0.0.1:3000',
```
