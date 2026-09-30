# [?] Fix test/contract.js `done` race condition (#3628)

## Summary
Severity: Unknown
Chain: Tooling
Component: web3/web3.js
Published: 2020-07-07
Source: https://github.com/web3/web3.js/commit/cbd0d064242cd6d8d214252d3f7f27fe710b88c6
Type: security-commit

## Details
Fix test/contract.js `done` race condition (#3628)

## Patch
### test/contract.js
```diff
@@ -3146,26 +3146,26 @@ describe('typical usage', function() {
         }
     });
 
-    it('should deploy a contract, sign transaction, and return contract instance', function (done) {
+    it('should deploy a contract, sign transaction, and return contract instance', async function () {
         var provider = new FakeIpcProvider();
         var eth = new Eth(provider);
         eth.accounts.wallet.add(account.privateKey);
 
+        const tx = await eth.accounts.wallet[0].signTransaction({
+            data: '0x1234567000000000000000000000000' + account.address.toLowerCase().replace('0x', '') + '00000000000000000000000000000000000000000000000000000000000000c8',
+            from: account.address.toLowerCase(),
+            gas: '0xd658',
+            gasPrice: '0xbb8',
+            chainId: '0x1',
+            nonce: '0x1',
+            chain: 'mainnet',
+            hardfork: 'petersburg'
+        });
+
         provider.injectValidation(function (payload) {
-            var expected = eth.accounts.wallet[0].signTransaction({
-                data: '0x1234567000000000000000000000000' + account.address.toLowerCase().replace('0x', '') + '00000000000000000000000000000000000000000000000000000000000000c8',
-                from: account.address.toLowerCase(),
-                gas: '0xd658',
-                gasPrice: '0xbb8',
-                chainId: '0x1',
-                nonce: '0x1',
-                chain: 'mainnet',
-                hardfork: 'petersburg'
-            }).then(function (tx) {
-                const expected = tx.rawTransaction;
-                assert.equal(payload.method, 'eth_sendRawTransaction');
-                assert.deepEqual(payload.params, [expected]);
-            });
+            const expected = tx.rawTransaction;
+            assert.equal(payload.method, 'eth_sendRawTransaction');
+            assert.deepEqual(payload.params, [expected]);
         });
 
         provider.injectResult('0x5550000000000000000000000000000000000000000000000000000000000032');
@@ -3211,39 +3211,41 @@ describe('typical usage', function() {
 
         var contract = new eth.Contract(abi);
 
-        contract.deploy({
-            data: '0x1234567',
-            arguments: [account.address, 200]
-        }).send({
-            from: account.address,
-            gas: 54872,
-            gasPrice: 3000,
-            chainId: 1,
-            nonce: 1,
-            chain: 'mainnet',
-            hardfork: 'petersburg'
-        })
+        let heardTxHashEvent = false;
+        let heardReceiptEvent = false;
+
+        await new Promise(function(resolve, reject){
+            contract.deploy({
+                data: '0x1234567',
+                arguments: [account.address, 200]
+            }).send({
+                from: account.address,
+                gas: 54872,
+                gasPrice: 3000,
+                chainId: 1,
+                nonce: 1,
+                chain: 'mainnet',
+                hardfork: 'petersburg'
+            })
             .on('transactionHash', function (value) {
                 assert.equal('0x5550000000000000000000000000000000000000000000000000000000000032', value);
+                heardTxHashEvent = true;
             })
             .on('receipt', function (receipt) {
                 assert.equal(address, receipt.contractAddress);
                 assert.isNull(contract.options.address);
+                heardReceiptEvent = true;
             })
             .then(function (newContract) {
-                // console.log(newContract);
                 assert.equal(newContract.options.address, address);
                 assert.isTrue(newContract !== contract, 'contract objects shouldn\'t the same');
-
-                done();
+                assert.isTrue(heardTxHashEvent, 'transactionHash event should have fired');
+                assert.isTrue(heardReceiptEvent, 'receipt event should have fired');
+                resolve();
             });
-        // .on('error', function (value) {
-        //     console.log('error', value);
-        //     done();
-        // });
-
-    }).timeout(10000);
-        // TODO add error check
+        });
+    });
+    // TODO add error check
 });
 
 describe('standalone usage', function() {
```
