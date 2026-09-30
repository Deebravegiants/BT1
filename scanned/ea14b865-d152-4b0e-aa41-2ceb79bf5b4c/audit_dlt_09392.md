# [?] bug-fix/signature validation vulnerability in case of contract signatures + dev notes

## Summary
Severity: Unknown
Chain: Biconomy
Component: bcnmy/scw-contracts
Published: 2023-01-10
Source: https://github.com/bcnmy/scw-contracts/commit/3441f4a0c2a9591f1df5f446eb44bde3d0130590
Type: security-commit

## Details
bug-fix/signature validation vulnerability in case of contract signatures + dev notes

## Patch
### contracts/smart-contract-wallet/SmartAccount.sol
```diff
@@ -310,7 +310,7 @@ contract SmartAccount is
         uint256 i = 0;
         address _signer;
         (v, r, s) = signatureSplit(signatures, i);
-        //review
+        //todo add the test case for contract signature
         if(v == 0) {
             // If v is 0 then it is a contract signature
             // When handling contract signatures the address of the contract is encoded into r
@@ -345,11 +345,10 @@ contract SmartAccount is
             // If v > 30 then default va (27,28) has been adjusted for eth_sign flow
             // To support eth_sign and similar we adjust v and hash the messageHash with the Ethereum message prefix before applying ecrecover
             _signer = ecrecover(keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", dataHash)), v - 4, r, s);
-            require(_signer == owner, "INVALID_SIGNATURE");
         } else {
             _signer = ecrecover(dataHash, v, r, s);
-            require(_signer == owner, "INVALID_SIGNATURE");
         }
+        require(_signer == owner, "INVALID_SIGNATURE");
     }
 
     /// @dev Allows to estimate a transaction.
```
