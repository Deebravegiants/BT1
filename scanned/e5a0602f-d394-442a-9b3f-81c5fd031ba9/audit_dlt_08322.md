# [?] fix: non-deterministic writeable account order (#21724)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-foundation/solana-web3.js
Published: 2022-01-08
Source: https://github.com/solana-foundation/solana-web3.js/commit/410780a41bbffb556e1d1f53d097934ffb56870f
Type: security-commit

## Details
fix: non-deterministic writeable account order (#21724)

## Patch
### src/transaction.ts
```diff
@@ -259,9 +259,12 @@ export class Transaction {
 
     // Sort. Prioritizing first by signer, then by writable
     accountMetas.sort(function (x, y) {
+      const pubkeySorting = x.pubkey
+        .toBase58()
+        .localeCompare(y.pubkey.toBase58());
       const checkSigner = x.isSigner === y.isSigner ? 0 : x.isSigner ? -1 : 1;
       const checkWritable =
-        x.isWritable === y.isWritable ? 0 : x.isWritable ? -1 : 1;
+        x.isWritable === y.isWritable ? pubkeySorting : x.isWritable ? -1 : 1;
       return checkSigner || checkWritable;
     });
 
```

### test/transaction.test.ts
```diff
@@ -5,7 +5,7 @@ import {expect} from 'chai';
 
 import {Keypair} from '../src/keypair';
 import {PublicKey} from '../src/publickey';
-import {Transaction} from '../src/transaction';
+import {Transaction, TransactionInstruction} from '../src/transaction';
 import {StakeProgram} from '../src/stake-program';
 import {SystemProgram} from '../src/system-program';
 import {Message} from '../src/message';
@@ -505,4 +505,86 @@ describe('Transaction', () => {
     tx.addSignature(from.publicKey, toBuffer(signature));
     expect(tx.verifySignatures()).to.be.true;
   });
+
+  it('can serialize, deserialize, and reserialize with a partial signer', () => {
+    const signer = Keypair.generate();
+    const acc0Writable = Keypair.generate();
+    const acc1Writable = Keypair.generate();
+    const acc2Writable = Keypair.generate();
+    const t0 = new Transaction({
+      recentBlockhash: 'HZaTsZuhN1aaz9WuuimCFMyH7wJ5xiyMUHFCnZSMyguH',
+      feePayer: signer.publicKey,
+    });
+    t0.add(
+      new TransactionInstruction({
+        keys: [
+          {
+            pubkey: signer.publicKey,
+            isWritable: true,
+            isSigner: true,
+          },
+          {
+            pubkey: acc0Writable.publicKey,
+            isWritable: true,
+            isSigner: false,
+          },
+        ],
+        programId: Keypair.generate().publicKey,
+      }),
+    );
+    t0.add(
+      new TransactionInstruction({
+        keys: [
+          {
+            pubkey: acc1Writable.publicKey,
+            isWritable: false,
+            isSigner: false,
+          },
+        ],
+        programId: Keypair.generate().publicKey,
+      }),
+    );
+    t0.add(
+      new TransactionInstruction({
+        keys: [
+          {
+            pubkey: acc2Writable.publicKey,
+            isWritable: true,
+            isSigner: false,
+          },
+        ],
+        programId: Keypair.generate().publicKey,
+      }),
+    );
+    t0.add(
+      new TransactionInstruction({
+        keys: [
+          {
+            pubkey: signer.publicKey,
+            isWritable: true,
+            isSigner: true,
+          },
+          {
+            pubkey: acc0Writable.publicKey,
+            isWritable: false,
+            isSigner: false,
+          },
+          {
+            pubkey: acc2Writable.publicKey,
+            isWritable: false,
+            isSigner: false,
+          },
+          {
+            pubkey: acc1Writable.publicKey,
+            isWritable: true,
+            isSigner: false,
+          },
+        ],
+        programId: Keypair.generate().publicKey,
+      }),
+    );
+    t0.partialSign(signer);
+    const t1 = Transaction.from(t0.serialize());
+    t1.serialize();
+  });
 });
```
