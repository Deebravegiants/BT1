# [?] fix: waitForTransactionReceipt race condition when polling many blocks (#3068)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2024-11-27
Source: https://github.com/wevm/viem/commit/c5768003785321628351b02156abe18291c9186c
Type: security-commit

## Details
fix: waitForTransactionReceipt race condition when polling many blocks (#3068)

## Patch
### .changeset/serious-cougars-serve.md
```diff
@@ -0,0 +1,5 @@
+---
+"viem": patch
+---
+
+Fixed `waitForTransactionReceipt` race condition when polling many blocks
```

### src/actions/public/waitForTransactionReceipt.test.ts
```diff
@@ -11,9 +11,13 @@ import { sendTransaction } from '../wallet/sendTransaction.js'
 
 import { anvilMainnet } from '../../../test/src/anvil.js'
 
-import { setIntervalMining } from '../index.js'
+import { sendRawTransaction, setIntervalMining, signTransaction } from '../index.js'
 import * as getBlock from './getBlock.js'
+import { prepareTransactionRequest } from '../../actions/index.js'
 import { waitForTransactionReceipt } from './waitForTransactionReceipt.js'
+import * as getTransactionModule from './getTransaction.js'
+import { privateKeyToAccount } from '~viem/accounts/privateKeyToAccount.js'
+import { keccak256 } from '~viem/utils/index.js'
 
 const client = anvilMainnet.getClient()
 
@@ -105,6 +109,81 @@ test('waits for transaction (multiple parallel)', async () => {
   expect(receipt_3).toEqual(receipt_4)
 })
 
+test('waits for transaction (polling many blocks while others waiting does not trigger race condition)', async () => {
+  const getTransaction = vi.spyOn(getTransactionModule, 'getTransaction')
+
+  // create a transaction to use it only as a template for the mocks
+
+  const templateHash = await sendTransaction(client, {
+    account: sourceAccount.address,
+    to: targetAccount.address,
+    value: parseEther('1'),
+  })
+  await mine(client, { blocks: 1 })
+  await wait(200)
+
+  const template = await getTransactionModule.getTransaction(client, { hash: templateHash })
+
+
+  // Prepare and calculate hash of problematic transaction. Will send it later
+
+  const prepareProblematic = await prepareTransactionRequest(client, {
+    account: privateKeyToAccount(accounts[0].privateKey),
+    to: targetAccount.address,
+    value: parseEther('1'),
+  })
+  const problematicTx = await signTransaction(client, prepareProblematic)
+  const problematicTxHash = keccak256(problematicTx)
+
+
+  // Prepare a good transaction. Will send it later
+
+  const prepareGood = await prepareTransactionRequest(client, {
+    account: privateKeyToAccount(accounts[0].privateKey),
+    to: targetAccount.address,
+    value: parseEther('0.0001'),
+    nonce: prepareProblematic.nonce + 1,
+  })
+  const goodTx = await signTransaction(client, prepareGood)
+  const goodTxHash = keccak256(goodTx)
+
+  // important step: we need to mock the getTransaction to simulate a transaction that is in the mempool but
+  // is not yet mined.
+  getTransaction.mockResolvedValueOnce({...template, hash: goodTxHash, nonce: 1233})
+
+  // Start looking for the receipt of the good transaction but did not send it yet. Here it will start polling 
+  const goodReceiptPromise = waitForTransactionReceipt(client, { hash: goodTxHash, timeout: 5000, retryCount: 0 })
+  await wait(200)
+
+  // to simulate a transaction that is in the mempool but not yet mined
+  getTransaction.mockResolvedValueOnce({...template, hash: problematicTxHash, nonce: 1234})
+
+  // Start polling the problematic transaction receipt
+  waitForTransactionReceipt(client, { hash: problematicTxHash, retryCount: 0 })
+  await mine(client, { blocks: 1 })
+  await wait(200)
+  
+  // Send the problematic transaction and mine it so we will have the receipt
+  await sendRawTransaction(client, { serializedTransaction: problematicTx })
+  await wait(200)
+
+  // important step: Mine a bunch of blocks together to trigger getTransactionReceipt many times for the same receipt.
+  // getting many receipt will trigger many unwatch from the same listener
+  await mine(client, { blocks: 1000 })
+  await wait(200)
+  
+  // Send good transaction and mine, if the polling is working fine should get the receipt but if not we will get a timeout.
+  await sendRawTransaction(client, { serializedTransaction: goodTx })
+  await mine(client, { blocks: 1 })
+  await wait(200)
+
+  await mine(client, { blocks: 1 })
+  await wait(200)
+
+  const {status} = await goodReceiptPromise
+  expect(status).toBe('success')
+})
+
 describe('replaced transactions', () => {
   test('repriced', async () => {
     setup()
```

### src/utils/observe.test.ts
```diff
@@ -174,3 +174,33 @@ test('cleans up emit function correctly', async () => {
 
   expect(active).toBe(false)
 })
+
+test('cleans up emit function when last listener unwatch', async () => {
+  const id = 'mock'
+  const callback = vi.fn()
+  const cleanup = vi.fn();
+  const emitter = vi.fn(({ emit }) => {
+    setTimeout(() => emit({ foo: 'bar' }), 100)
+    return () => {
+      cleanup()
+    }
+  })
+
+  const unwatch1 = observe(id, { emit: () => {
+    unwatch1();
+    unwatch1();
+    unwatch1();
+  } }, emitter)
+
+  const unwatch2 = observe(id, { emit: callback }, emitter)
+
+  await wait(110)
+
+  // Make sure there is no premature call to cleanup
+  // as watch2 listener is still subscribed
+  expect(cleanup).not.toHaveBeenCalled()
+
+  unwatch2()
+
+  expect(cleanup).toHaveBeenCalledTimes(1)
+})
```

### src/utils/observe.ts
```diff
@@ -43,6 +43,7 @@ export function observe<callbacks extends Callbacks>(
   }
 
   const unwatch = () => {
+    if (!getListeners().find((cb: any) => cb.id === callbackId)) return
     const cleanup = cleanupCache.get(observerId)
     if (getListeners().length === 1 && cleanup) cleanup()
     unsubscribe()
```
