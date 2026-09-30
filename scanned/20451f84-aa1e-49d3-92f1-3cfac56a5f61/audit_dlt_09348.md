# [?] fix: waitForTransactionReceipt unwatch race condition

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2023-07-02
Source: https://github.com/wevm/viem/commit/29693f7087fa4504cc63fd3fb1be43f62927200a
Type: security-commit

## Details
fix: waitForTransactionReceipt unwatch race condition

## Patch
### src/actions/public/waitForTransactionReceipt.test.ts
```diff
@@ -41,6 +41,54 @@ test('waits for transaction (send -> mine -> wait)', async () => {
   expect(status).toBe('success')
 })
 
+test('waits for transaction (multiple waterfall)', async () => {
+  const hash = await sendTransaction(walletClient, {
+    account: sourceAccount.address,
+    to: targetAccount.address,
+    value: parseEther('1'),
+  })
+  const receipt_1 = await waitForTransactionReceipt(publicClient, {
+    hash,
+  })
+  const receipt_2 = await waitForTransactionReceipt(publicClient, {
+    hash,
+  })
+  const receipt_3 = await waitForTransactionReceipt(publicClient, {
+    hash,
+  })
+  const receipt_4 = await waitForTransactionReceipt(publicClient, {
+    hash,
+  })
+  expect(receipt_1).toEqual(receipt_2)
+  expect(receipt_2).toEqual(receipt_3)
+  expect(receipt_3).toEqual(receipt_4)
+})
+
+test('waits for transaction (multiple parallel)', async () => {
+  const hash = await sendTransaction(walletClient, {
+    account: sourceAccount.address,
+    to: targetAccount.address,
+    value: parseEther('1'),
+  })
+  const [receipt_1, receipt_2, receipt_3, receipt_4] = await Promise.all([
+    waitForTransactionReceipt(publicClient, {
+      hash,
+    }),
+    waitForTransactionReceipt(publicClient, {
+      hash,
+    }),
+    waitForTransactionReceipt(publicClient, {
+      hash,
+    }),
+    waitForTransactionReceipt(publicClient, {
+      hash,
+    }),
+  ])
+  expect(receipt_1).toEqual(receipt_2)
+  expect(receipt_2).toEqual(receipt_3)
+  expect(receipt_3).toEqual(receipt_4)
+})
+
 describe('replaced transactions', () => {
   test('repriced', async () => {
     await mine(testClient, { blocks: 10 })
```

### src/actions/public/waitForTransactionReceipt.ts
```diff
@@ -126,7 +126,7 @@ export async function waitForTransactionReceipt<
       observerId,
       { onReplaced, resolve, reject },
       (emit) => {
-        const unwatch = watchBlockNumber(client, {
+        const _unwatch = watchBlockNumber(client, {
           emitMissed: true,
           emitOnBegin: true,
           poll: true,
@@ -136,8 +136,8 @@ export async function waitForTransactionReceipt<
 
             let blockNumber = blockNumber_
 
-            const done = async (fn: () => void) => {
-              unwatch()
+            const done = (fn: () => void) => {
+              _unwatch()
               fn()
               _unobserve()
             }
@@ -248,7 +248,6 @@ export async function waitForTransactionReceipt<
             }
           },
         })
-        return unwatch
       },
     )
   })
```
