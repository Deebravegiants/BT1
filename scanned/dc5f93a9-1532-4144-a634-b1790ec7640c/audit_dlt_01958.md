# [?] ethereum: deploy test token nonce race condition fix

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2022-10-28
Source: https://github.com/wormhole-foundation/wormhole/commit/25d2f24b03a0fa29629fe8fbb3a2c918fb49834b
Type: security-commit

## Details
ethereum: deploy test token nonce race condition fix

Noticed this error happening in tilt sometimes:

[tests] Error: Returned error: VM Exception while processing transaction: the tx
doesn't have the correct nonce. account has nonce of: 17 tx has nonce of: 16

It's not safe to submit txs in parallel, because the nonce can get out of sync.
Instead we should submit them serially.

## Patch
### ethereum/scripts/deploy_test_token.js
```diff
@@ -16,27 +16,22 @@ const interateToStandardTransactionCount = async () => {
   );
 
   const transactionsToBurn = 32 - transactionCount;
-  const promises = [];
   for (let i = 0; i < transactionsToBurn; i++) {
-    promises.push(
-      web3.eth.sendTransaction({
-        to: accounts[0],
-        from: accounts[0],
-        value: 530,
-      })
-    );
+    await web3.eth.sendTransaction({
+      to: accounts[0],
+      from: accounts[0],
+      value: 530,
+    })
   }
 
-  await Promise.all(promises);
-
   const burnCount = await web3.eth.getTransactionCount(accounts[0], "latest");
 
   console.log("transaction count after burn: ", burnCount);
 
   return Promise.resolve();
 };
 
-module.exports = async function(callback) {
+module.exports = async function (callback) {
   try {
     const accounts = await web3.eth.getAccounts();
 
```
