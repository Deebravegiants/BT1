# [?] Fix ECDSA signature malleability (#3610)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2022-08-10
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/d693d89d99325f395182e4f547dbf5ff8e5c3c87
Type: security-commit

## Details
Fix ECDSA signature malleability (#3610)

## Patch
### CHANGELOG.md
```diff
@@ -18,6 +18,12 @@
 
 ERC-721 integrators that interpret contract state from events should make sure that they implement the clearing of approval that is implicit in every transfer according to the EIP. Previous versions of OpenZeppellin Contracts emitted an explicit `Approval` event even though it was not required by the specification, and this is no longer the case.
 
+## 4.7.3
+
+### Breaking changes
+
+ * `ECDSA`: `recover(bytes32,bytes)` and `tryRecover(bytes32,bytes)` no longer accept compact signatures to prevent malleability. Compact signature support remains available using `recover(bytes32,bytes32,bytes32)` and `tryRecover(bytes32,bytes32,bytes32)`.
+
 ## 4.7.2
 
  * `LibArbitrumL2`, `CrossChainEnabledArbitrumL2`: Fixed detection of cross-chain calls for EOAs. Previously, calls from EOAs would be classified as cross-chain calls. ([#3578](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3578))
```

### contracts/utils/cryptography/ECDSA.sol
```diff
@@ -55,9 +55,6 @@ library ECDSA {
      * _Available since v4.3._
      */
     function tryRecover(bytes32 hash, bytes memory signature) internal pure returns (address, RecoverError) {
-        // Check the signature length
-        // - case 65: r,s,v signature (standard)
-        // - case 64: r,vs signature (cf https://eips.ethereum.org/EIPS/eip-2098) _Available since v4.1._
         if (signature.length == 65) {
             bytes32 r;
             bytes32 s;
@@ -71,17 +68,6 @@ library ECDSA {
                 v := byte(0, mload(add(signature, 0x60)))
             }
             return tryRecover(hash, v, r, s);
-        } else if (signature.length == 64) {
-            bytes32 r;
-            bytes32 vs;
-            // ecrecover takes the signature parameters, and the only way to get them
-            // currently is to use assembly.
-            /// @solidity memory-safe-assembly
-            assembly {
-                r := mload(add(signature, 0x20))
-                vs := mload(add(signature, 0x40))
-            }
-            return tryRecover(hash, r, vs);
         } else {
             return (address(0), RecoverError.InvalidSignatureLength);
         }
```

### test/utils/cryptography/ECDSA.test.js
```diff
@@ -22,16 +22,6 @@ function to2098Format (signature) {
   return web3.utils.bytesToHex(short);
 }
 
-function from2098Format (signature) {
-  const short = web3.utils.hexToBytes(signature);
-  if (short.length !== 64) {
-    throw new Error('invalid signature length (expected short format)');
-  }
-  short.push((short[32] >> 7) + 27);
-  short[32] &= (1 << 7) - 1; // zero out the first bit of 1 the 32nd byte
-  return web3.utils.bytesToHex(short);
-}
-
 function split (signature) {
   const raw = web3.utils.hexToBytes(signature);
   switch (raw.length) {
@@ -144,11 +134,13 @@ contract('ECDSA', function (accounts) {
         );
       });
 
-      it('works with short EIP2098 format', async function () {
+      it('rejects short EIP2098 format', async function () {
         const version = '1b'; // 27 = 1b.
         const signature = signatureWithoutVersion + version;
-        expect(await this.ecdsa.recover(TEST_MESSAGE, to2098Format(signature))).to.equal(signer);
-        expect(await this.ecdsa.recover(TEST_MESSAGE, from2098Format(to2098Format(signature)))).to.equal(signer);
+        await expectRevert(
+          this.ecdsa.recover(TEST_MESSAGE, to2098Format(signature)),
+          'ECDSA: invalid signature length',
+        );
       });
     });
 
@@ -187,11 +179,13 @@ contract('ECDSA', function (accounts) {
         );
       });
 
-      it('works with short EIP2098 format', async function () {
+      it('rejects short EIP2098 format', async function () {
         const version = '1c'; // 27 = 1b.
         const signature = signatureWithoutVersion + version;
-        expect(await this.ecdsa.recover(TEST_MESSAGE, to2098Format(signature))).to.equal(signer);
-        expect(await this.ecdsa.recover(TEST_MESSAGE, from2098Format(to2098Format(signature)))).to.equal(signer);
+        await expectRevert(
+          this.ecdsa.recover(TEST_MESSAGE, to2098Format(signature)),
+          'ECDSA: invalid signature length',
+        );
       });
     });
 
```
