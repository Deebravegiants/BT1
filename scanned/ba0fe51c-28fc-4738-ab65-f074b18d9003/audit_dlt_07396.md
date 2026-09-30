# [?] Signature Malleability: (#1622)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2019-03-07
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/79dd498b16b957399f84b9aa7e720f98f9eb83e3
Type: security-commit

## Details
Signature Malleability: (#1622)

* Transaction Malleability:
If you allow for both values 0/1 and 27/28, you allow two different
signatures both resulting in a same valid recovery. (r,s,0/1) and
(r,s,27/28) would both be valid, recover the same public key and sign
the same data. Furthermore, given (r,s,0/1), (r,s,27/28) can be
constructed by anyone.

* Transaction Malleability:
EIP-2 still allows signature malleabality for ecrecover(), remove this
possibility and force the signature to be unique.

* Added a reference to appendix F to the yellow paper and improved
comment.

* better test description for testing the version 0, which returns
a zero address

* Check that the conversion from 0/1 to 27/28 only happens if its 0/1

* improved formatting

* Refactor ECDSA code a bit.

* Refactor ECDSA tests a bit.

* Add changelog entry.

* Add high-s check test.

## Patch
### CHANGELOG.md
```diff
@@ -13,6 +13,7 @@
  * Upgraded the minimum compiler version to v0.5.2: this removes many Solidity warnings that were false positives. ([#1606](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1606))
  * `Counter`'s API has been improved, and is now used by `ERC721` (though it is still in `drafts`). ([#1610](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1610))
  * `ERC721`'s transfers are now more gas efficient due to removal of unnecessary `SafeMath` calls. ([#1610](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1610))
+ * `ECDSA`: `recover` no longer accepts malleable signatures (those using upper-range values for `s`, or 0/1 for `v`). ([#1622](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1622))
  * Fixed variable shadowing issues. ([#1606](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1606))
 
 ### Bugfixes:
```

### contracts/cryptography/ECDSA.sol
```diff
@@ -14,16 +14,16 @@ library ECDSA {
      * @param signature bytes signature, the signature is generated using web3.eth.sign()
      */
     function recover(bytes32 hash, bytes memory signature) internal pure returns (address) {
-        bytes32 r;
-        bytes32 s;
-        uint8 v;
-
         // Check the signature length
         if (signature.length != 65) {
             return (address(0));
         }
 
         // Divide the signature in r, s and v variables
+        bytes32 r;
+        bytes32 s;
+        uint8 v;
+
         // ecrecover takes the signature parameters, and the only way to get them
         // currently is to use assembly.
         // solhint-disable-next-line no-inline-assembly
@@ -33,17 +33,25 @@ library ECDSA {
             v := byte(0, mload(add(signature, 0x60)))
         }
 
-        // Version of signature should be 27 or 28, but 0 and 1 are also possible versions
-        if (v < 27) {
-            v += 27;
+        // EIP-2 still allows signature malleability for ecrecover(). Remove this possibility and make the signature
+        // unique. Appendix F in the Ethereum Yellow paper (https://ethereum.github.io/yellowpaper/paper.pdf), defines
+        // the valid range for s in (281): 0 < s < secp256k1n ÷ 2 + 1, and for v in (282): v ∈ {27, 28}. Most
+        // signatures from current libraries generate a unique signature with an s-value in the lower half order.
+        //
+        // If your library generates malleable signatures, such as s-values in the upper range, calculate a new s-value
+        // with 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 - s1 and flip v from 27 to 28 or
+        // vice versa. If your library also generates signatures with 0/1 for v instead 27/28, add 27 to v to accept
+        // these malleable signatures as well.
+        if (uint256(s) > 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0) {
+            return address(0);
         }
 
-        // If the version is correct return the signer address
         if (v != 27 && v != 28) {
-            return (address(0));
-        } else {
-            return ecrecover(hash, v, r, s);
+            return address(0);
         }
+
+        // If the signature is valid (and not malleable), return the signer address
+        return ecrecover(hash, v, r, s);
     }
 
     /**
```

### test/cryptography/ECDSA.test.js
```diff
@@ -1,5 +1,6 @@
-const { shouldFail } = require('openzeppelin-test-helpers');
-const { signMessage, toEthSignedMessageHash } = require('../helpers/sign');
+const { constants, shouldFail } = require('openzeppelin-test-helpers');
+const { ZERO_ADDRESS } = constants;
+const { toEthSignedMessageHash, fixSignature } = require('../helpers/sign');
 
 const ECDSAMock = artifacts.require('ECDSAMock');
 
@@ -19,10 +20,10 @@ contract('ECDSA', function ([_, anyone]) {
       const signatureWithoutVersion = '0x5d99b6f7f6d1f73d1a26497f2b1c89b24c0993913f86e9a2d02cd69887d9c94f3c880358579d811b21dd1b7fd9bb01c1d81d10e69f0384e675c32b39643be892';
 
       context('with 00 as version value', function () {
-        it('works', async function () {
+        it('returns 0', async function () {
           const version = '00';
           const signature = signatureWithoutVersion + version;
-          (await this.ecdsa.recover(TEST_MESSAGE, signature)).should.equal(signer);
+          (await this.ecdsa.recover(TEST_MESSAGE, signature)).should.equal(ZERO_ADDRESS);
         });
       });
 
@@ -40,8 +41,7 @@ contract('ECDSA', function ([_, anyone]) {
           // The only valid values are 0, 1, 27 and 28.
           const version = '02';
           const signature = signatureWithoutVersion + version;
-          (await this.ecdsa.recover(TEST_MESSAGE, signature)).should.equal(
-            '0x0000000000000000000000000000000000000000');
+          (await this.ecdsa.recover(TEST_MESSAGE, signature)).should.equal(ZERO_ADDRESS);
         });
       });
     });
@@ -52,14 +52,14 @@ contract('ECDSA', function ([_, anyone]) {
       const signatureWithoutVersion = '0x331fe75a821c982f9127538858900d87d3ec1f9f737338ad67cad133fa48feff48e6fa0c18abc62e42820f05943e47af3e9fbe306ce74d64094bdf1691ee53e0';
 
       context('with 01 as version value', function () {
-        it('works', async function () {
+        it('returns 0', async function () {
           const version = '01';
           const signature = signatureWithoutVersion + version;
-          (await this.ecdsa.recover(TEST_MESSAGE, signature)).should.equal(signer);
+          (await this.ecdsa.recover(TEST_MESSAGE, signature)).should.equal(ZERO_ADDRESS);
         });
       });
 
-      context('with 28 signature', function () {
+      context('with 28 as version value', function () {
         it('works', async function () {
           const version = '1c'; // 28 = 1c.
           const signature = signatureWithoutVersion + version;
@@ -73,17 +73,26 @@ contract('ECDSA', function ([_, anyone]) {
           // The only valid values are 0, 1, 27 and 28.
           const version = '02';
           const signature = signatureWithoutVersion + version;
-          (await this.ecdsa.recover(TEST_MESSAGE, signature)).should.equal(
-            '0x0000000000000000000000000000000000000000');
+          (await this.ecdsa.recover(TEST_MESSAGE, signature)).should.equal(ZERO_ADDRESS);
         });
       });
     });
 
+    context('with high-s value signature', function () {
+      it('returns 0', async function () {
+        const message = '0xb94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9';
+        // eslint-disable-next-line max-len
+        const highSSignature = '0xe742ff452d41413616a5bf43fe15dd88294e983d3d36206c2712f39083d638bde0a0fc89be718fbc1033e1d30d78be1c68081562ed2e97af876f286f3453231d1b';
+
+        (await this.ecdsa.recover(message, highSSignature)).should.equal(ZERO_ADDRESS);
+      });
+    });
+
     context('using web3.eth.sign', function () {
       context('with correct signature', function () {
         it('returns signer address', async function () {
           // Create the signature
-          const signature = await signMessage(anyone, TEST_MESSAGE);
+          const signature = fixSignature(await web3.eth.sign(TEST_MESSAGE, anyone));
 
           // Recover the signer address from the generated message and signature.
           (await this.ecdsa.recover(
@@ -96,23 +105,23 @@ contract('ECDSA', function ([_, anyone]) {
       context('with wrong signature', function () {
         it('does not return signer address', async function () {
           // Create the signature
-          const signature = await signMessage(anyone, TEST_MESSAGE);
+          const signature = await web3.eth.sign(TEST_MESSAGE, anyone);
 
           // Recover the signer address from the generated message and wrong signature.
           (await this.ecdsa.recover(WRONG_MESSAGE, signature)).should.not.equal(anyone);
         });
       });
     });
-  });
 
-  context('with small hash', function () {
-    // @TODO - remove `skip` once we upgrade to solc^0.5
-    it.skip('reverts', async function () {
-      // Create the signature
-      const signature = await signMessage(anyone, TEST_MESSAGE);
-      await shouldFail.reverting(
-        this.ecdsa.recover(TEST_MESSAGE.substring(2), signature)
-      );
+    context('with small hash', function () {
+      // @TODO - remove `skip` once we upgrade to solc^0.5
+      it.skip('reverts', async function () {
+        // Create the signature
+        const signature = await web3.eth.sign(TEST_MESSAGE, anyone);
+        await shouldFail.reverting(
+          this.ecdsa.recover(TEST_MESSAGE.substring(2), signature)
+        );
+      });
     });
   });
 
```

### test/helpers/sign.js
```diff
@@ -9,9 +9,21 @@ function toEthSignedMessageHash (messageHex) {
   return web3.utils.sha3(Buffer.concat([prefix, messageBuffer]));
 }
 
+function fixSignature (signature) {
+  // in geth its always 27/28, in ganache its 0/1. Change to 27/28 to prevent
+  // signature malleability if version is 0/1
+  // see https://github.com/ethereum/go-ethereum/blob/v1.8.23/internal/ethapi/api.go#L465
+  let v = parseInt(signature.slice(130, 132), 16);
+  if (v < 27) {
+    v += 27;
+  }
+  const vHex = v.toString(16);
+  return signature.slice(0, 130) + vHex;
+}
+
 // signs message in node (ganache auto-applies "Ethereum Signed Message" prefix)
-const signMessage = (signer, messageHex = '0x') => {
-  return web3.eth.sign(messageHex, signer);
+async function signMessage (signer, messageHex = '0x') {
+  return fixSignature(await web3.eth.sign(messageHex, signer));
 };
 
 /**
@@ -50,5 +62,6 @@ const getSignFor = (contract, signer) => (redeemer, methodName, methodArgs = [])
 module.exports = {
   signMessage,
   toEthSignedMessageHash,
+  fixSignature,
   getSignFor,
 };
```
