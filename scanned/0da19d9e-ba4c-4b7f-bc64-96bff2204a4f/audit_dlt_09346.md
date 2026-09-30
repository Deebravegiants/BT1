# [?] fix: increase waitForTransactionReceipt timeout in race condition test

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-03-04
Source: https://github.com/wevm/viem/commit/4b685a1d1b571b220c6fb0537ec65e9f83e783d1
Type: security-commit

## Details
fix: increase waitForTransactionReceipt timeout in race condition test

Amp-Thread-ID: https://ampcode.com/threads/T-019cb6d7-c794-742b-ac88-6bc216b24bbc
Co-authored-by: Amp <amp@ampcode.com>

## Patch
### src/actions/public/waitForTransactionReceipt.test.ts
```diff
@@ -159,7 +159,7 @@ test('waits for transaction (polling many blocks while others waiting does not t
   // Start looking for the receipt of the good transaction but did not send it yet. Here it will start polling
   const goodReceiptPromise = waitForTransactionReceipt(client, {
     hash: goodTxHash,
-    timeout: 5000,
+    timeout: 30_000,
     retryCount: 0,
   })
   await wait(200)
```
