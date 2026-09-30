# [?] Merge branch 'c4-remediations' into 2023-03-16-Reentrancy-Guard-Custom

## Summary
Severity: Unknown
Chain: Biconomy
Component: bcnmy/scw-contracts
Published: 2023-03-16
Source: https://github.com/bcnmy/scw-contracts/commit/b06a8443889994b66a5ba8d74a028cfa53fa2c6d
Type: security-commit

## Details
Merge branch 'c4-remediations' into 2023-03-16-Reentrancy-Guard-Custom

## Patch
### contracts/smart-contract-wallet/SmartAccount.sol
```diff
@@ -8,10 +8,12 @@ import {SignatureDecoder} from "./common/SignatureDecoder.sol";
 import {SecuredTokenTransfer} from "./common/SecuredTokenTransfer.sol";
 import {LibAddress} from "./libs/LibAddress.sol";
 import {ISignatureValidator, ISignatureValidatorConstants} from "./interfaces/ISignatureValidator.sol";
+import {Math} from "./libs/Math.sol";
 import {IERC165} from "./interfaces/IERC165.sol";
 import {ReentrancyGuard} from "./common/ReentrancyGuard.sol";
 import {SmartAccountErrors} from "./common/Errors.sol";
 import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
+import {IModule} from "./test/IModule.sol";
 
 contract SmartAccount is
     BaseSmartAccount,
@@ -231,14 +233,6 @@ contract SmartAccount is
         _setupModules(address(0), bytes(""));
     }
 
-    // @review: max and min use from Math.sol instead of re-implemented in the contracts
-    /**
-     * @dev Returns the largest of two numbers.
-     */
-    function max(uint256 a, uint256 b) internal pure returns (uint256) {
-        return a >= b ? a : b;
-    }
-
     /**
      * @dev Gnosis style transaction with optional repay in native tokens OR ERC20
      * @dev Allows to execute a transaction confirmed by required signature/s and then pays the account that submitted the transaction.
@@ -274,11 +268,12 @@ contract SmartAccount is
         // Bitshift left 6 bits means multiplying by 64, just more gas efficient
         if (
             gasleft() <
-            max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) + 500
+            Math.max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) + 500
         )
             revert NotEnoughGasLeft(
                 gasleft(),
-                max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) + 500
+                Math.max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) +
+                    500
             );
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
         {
@@ -754,7 +749,8 @@ contract SmartAccount is
                     userOpData[4:],
                     (address, uint, bytes)
                 );
-                if (address(modules[_to]) != address(0)) return 0;
+                if (address(modules[_to]) != address(0))
+                    return IModule(_to).validateSignature(userOp, userOpHash);
             }
         }
         bytes32 hash = userOpHash.toEthSignedMessageHash();
```

### contracts/smart-contract-wallet/SmartAccountNoAuth.sol
```diff
@@ -180,13 +180,6 @@ contract SmartAccountNoAuth is
         _setupModules(address(0), bytes(""));
     }
 
-    /**
-     * @dev Returns the largest of two numbers.
-     */
-    function max(uint256 a, uint256 b) internal pure returns (uint256) {
-        return a >= b ? a : b;
-    }
-
     // Gnosis style transaction with optional repay in native tokens OR ERC20
     /// @dev Allows to execute a Safe transaction confirmed by required number of owners and then pays the account that submitted the transaction.
     /// Note: The fees are always transferred, even if the user transaction fails.
@@ -220,7 +213,8 @@ contract SmartAccountNoAuth is
         // Bitshift left 6 bits means multiplying by 64, just more gas efficient
         require(
             gasleft() >=
-                max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) + 500,
+                Math.max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) +
+                    500,
             "BSA010"
         );
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
```

### contracts/smart-contract-wallet/libs/Math.sol
```diff
@@ -71,6 +71,9 @@ library Math {
 
             // Handle non-overflow cases, 256 by 256 division.
             if (prod1 == 0) {
+                // Solidity will revert if denominator == 0, unlike the div opcode on its own.
+                // The surrounding unchecked block does not change this fact.
+                // See https://docs.soliditylang.org/en/latest/control-structures.html#checked-or-unchecked-arithmetic.
                 return prod0 / denominator;
             }
 
```

### contracts/smart-contract-wallet/test/IModule.sol
```diff
@@ -0,0 +1,17 @@
+// SPDX-License-Identifier: MIT
+pragma solidity 0.8.17;
+import {UserOperation} from "@account-abstraction/contracts/interfaces/UserOperation.sol";
+
+// interface for modules to verify singatures signed over userOpHash
+interface IModule {
+    /**
+     * @dev standard validateSignature for modules to validate and mark userOpHash as seen
+     * @param userOp the operation that is about to be executed.
+     * @param userOpHash hash of the user's request data. can be used as the basis for signature.
+     * @return sigValidationResult sigAuthorizer to be passed back to trusting Account, aligns with validationData
+     */
+    function validateSignature(
+        UserOperation calldata userOp,
+        bytes32 userOpHash
+    ) external returns (uint256 sigValidationResult);
+}
```

### contracts/smart-contract-wallet/test/MaliciousAccount2.sol
```diff
@@ -174,13 +174,6 @@ contract MaliciousAccount2 is
         _setupModules(address(0), bytes(""));
     }
 
-    /**
-     * @dev Returns the largest of two numbers.
-     */
-    function max(uint256 a, uint256 b) internal pure returns (uint256) {
-        return a >= b ? a : b;
-    }
-
     // Gnosis style transaction with optional repay in native tokens OR ERC20
     /// @dev Allows to execute a Safe transaction confirmed by required number of owners and then pays the account that submitted the transaction.
     /// Note: The fees are always transferred, even if the user transaction fails.
@@ -214,7 +207,8 @@ contract MaliciousAccount2 is
         // Bitshift left 6 bits means multiplying by 64, just more gas efficient
         require(
             gasleft() >=
-                max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) + 500,
+                Math.max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) +
+                    500,
             "BSA010"
         );
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
```

### contracts/smart-contract-wallet/test/SocialRecoveryModule.sol
```diff
@@ -1,10 +1,19 @@
 // SPDX-License-Identifier: MIT
 pragma solidity 0.8.17;
 import "../SmartAccount.sol";
+import {IModule} from "./IModule.sol";
 
-contract SocialRecoveryModule {
+contract SocialRecoveryModule is IModule {
     string public constant NAME = "Social Recovery Module";
     string public constant VERSION = "0.1.0";
+    uint256 internal constant SIG_VALIDATION_FAILED = 1;
+
+    // @review
+    // Might as well keep a state to mark seen userOpHashes
+    mapping(bytes32 => bool) public opsSeen;
+
+    // @todo
+    // Notice validateAndUpdateNonce in just skipped in case of modules. To avoid replay of same userOpHash I think it should be done.
 
     struct Friends {
         address[] friends; // the list of friends
@@ -42,6 +51,22 @@ contract SocialRecoveryModule {
         entry.threshold = _threshold;
     }
 
+    /**
+     * @dev standard validateSignature for modules to validate and mark userOpHash as seen
+     * @param userOp the operation that is about to be executed.
+     * @param userOpHash hash of the user's request data. can be used as the basis for signature.
+     * @return sigValidationResult sigAuthorizer to be passed back to trusting Account, aligns with validationData
+     */
+    function validateSignature(
+        UserOperation calldata userOp,
+        bytes32 userOpHash
+    ) external virtual returns (uint256 sigValidationResult) {
+        if (opsSeen[userOpHash] == true) return SIG_VALIDATION_FAILED;
+        opsSeen[userOpHash] = true;
+        // can perform it's own access control logic, verify agaisnt expected signer and return SIG_VALIDATION_FAILED
+        return 0;
+    }
+
     /**
      * @dev Confirm friend recovery transaction. Only by friends.
      */
```

### contracts/smart-contract-wallet/test/WhitelistModule.sol
```diff
@@ -1,10 +1,19 @@
 // SPDX-License-Identifier: Apache-2.0
 pragma solidity 0.8.17;
 import "../SmartAccount.sol";
+import {IModule} from "./IModule.sol";
 
 contract WhitelistModule {
     mapping(address => bool) public whitelisted;
     address public moduleOwner;
+    uint256 internal constant SIG_VALIDATION_FAILED = 1;
+
+    // @review
+    // Might as well keep a state to mark seen userOpHashes
+    mapping(bytes32 => bool) public opsSeen;
+
+    // @todo
+    // Notice validateAndUpdateNonce in just skipped in case of modules. To avoid replay of same userOpHash I think it should be done.
 
     constructor(address _owner) {
         moduleOwner = _owner;
@@ -23,6 +32,22 @@ contract WhitelistModule {
         whitelisted[_target] = true;
     }
 
+    /**
+     * @dev standard validateSignature for modules to validate and mark userOpHash as seen
+     * @param userOp the operation that is about to be executed.
+     * @param userOpHash hash of the user's request data. can be used as the basis for signature.
+     * @return sigValidationResult sigAuthorizer to be passed back to trusting Account, aligns with validationData
+     */
+    function validateSignature(
+        UserOperation calldata userOp,
+        bytes32 userOpHash
+    ) external virtual returns (uint256 sigValidationResult) {
+        if (opsSeen[userOpHash] == true) return SIG_VALIDATION_FAILED;
+        opsSeen[userOpHash] = true;
+        // can perform it's own access control logic, verify agaisnt expected signer and return SIG_VALIDATION_FAILED
+        return 0;
+    }
+
     function authCall(
         SmartAccount _account,
         address payable _to,
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount10.sol
```diff
@@ -194,13 +194,7 @@ contract SmartAccount10 is
         _setupModules(address(0), bytes(""));
     }
 
-    /**
-     * @dev Returns the largest of two numbers.
-     */
-    function max(uint256 a, uint256 b) internal pure returns (uint256) {
-        return a >= b ? a : b;
-    }
-
+    // review: batchId should be carefully designed or removed all together (including 2D nonces)
     // Gnosis style transaction with optional repay in native tokens OR ERC20
     /// @dev Allows to execute a Safe transaction confirmed by required number of owners and then pays the account that submitted the transaction.
     /// Note: The fees are always transferred, even if the user transaction fails.
@@ -233,7 +227,8 @@ contract SmartAccount10 is
         // We also include the 1/64 in the check that is not send along with a call to counteract potential shortings because of EIP-150
         require(
             gasleft() >=
-                max((_tx.targetTxGas * 64) / 63, _tx.targetTxGas + 2500) + 500,
+                Math.max((_tx.targetTxGas * 64) / 63, _tx.targetTxGas + 2500) +
+                    500,
             "BSA010"
         );
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount2.sol
```diff
@@ -51,7 +51,8 @@ contract SmartAccount2 is SmartAccount {
         // Bitshift left 6 bits means multiplying by 64, just more gas efficient
         require(
             gasleft() >=
-                max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) + 500,
+                Math.max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) +
+                    500,
             "BSA010"
         );
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount3.sol
```diff
@@ -12,7 +12,6 @@ import {SmartAccountErrors} from "../../common/Errors.sol";
 import "../../interfaces/ISignatureValidator.sol";
 import "../../interfaces/IERC165.sol";
 import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
-import "hardhat/console.sol";
 
 
 contract SmartAccount3 is
@@ -186,13 +185,6 @@ contract SmartAccount3 is
         _setupModules(address(0), bytes(""));
     }
 
-    /**
-     * @dev Returns the largest of two numbers.
-     */
-    function max(uint256 a, uint256 b) internal pure returns (uint256) {
-        return a >= b ? a : b;
-    }
-
     function getImplementation()
         external
         view
@@ -237,7 +229,8 @@ contract SmartAccount3 is
         // Bitshift left 6 bits means multiplying by 64, just more gas efficient
         require(
             gasleft() >=
-                max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) + 500,
+                Math.max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) +
+                    500,
             "BSA010"
         );
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
@@ -270,7 +263,6 @@ contract SmartAccount3 is
                 );
                 emit AccountHandlePayment(txHash, payment);
             }
-            console.log("goes from v3");
         }
     }
 
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount4.sol
```diff
@@ -192,13 +192,7 @@ contract SmartAccount4 is
         _setupModules(address(0), bytes(""));
     }
 
-    /**
-     * @dev Returns the largest of two numbers.
-     */
-    function max(uint256 a, uint256 b) internal pure returns (uint256) {
-        return a >= b ? a : b;
-    }
-
+    // review: batchId should be carefully designed or removed all together (including 2D nonces)
     // Gnosis style transaction with optional repay in native tokens OR ERC20
     /// @dev Allows to execute a Safe transaction confirmed by required number of owners and then pays the account that submitted the transaction.
     /// Note: The fees are always transferred, even if the user transaction fails.
@@ -231,7 +225,8 @@ contract SmartAccount4 is
         // We also include the 1/64 in the check that is not send along with a call to counteract potential shortings because of EIP-150
         require(
             gasleft() >=
-                max((_tx.targetTxGas * 64) / 63, _tx.targetTxGas + 2500) + 500,
+                Math.max((_tx.targetTxGas * 64) / 63, _tx.targetTxGas + 2500) +
+                    500,
             "BSA010"
         );
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
@@ -264,7 +259,6 @@ contract SmartAccount4 is
                 );
                 emit AccountHandlePayment(txHash, payment);
             }
-            console.log("has to go through new v4 implementation");
         }
     }
 
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount5.sol
```diff
@@ -192,13 +192,7 @@ contract SmartAccount5 is
         _setupModules(address(0), bytes(""));
     }
 
-    /**
-     * @dev Returns the largest of two numbers.
-     */
-    function max(uint256 a, uint256 b) internal pure returns (uint256) {
-        return a >= b ? a : b;
-    }
-
+    // review: batchId should be carefully designed or removed all together (including 2D nonces)
     // Gnosis style transaction with optional repay in native tokens OR ERC20
     /// @dev Allows to execute a Safe transaction confirmed by required number of owners and then pays the account that submitted the transaction.
     /// Note: The fees are always transferred, even if the user transaction fails.
@@ -232,7 +226,8 @@ contract SmartAccount5 is
         // We also include the 1/64 in the check that is not send along with a call to counteract potential shortings because of EIP-150
         require(
             gasleft() >=
-                max((_tx.targetTxGas * 64) / 63, _tx.targetTxGas + 2500) + 500,
+                Math.max((_tx.targetTxGas * 64) / 63, _tx.targetTxGas + 2500) +
+                    500,
             "BSA010"
         );
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
```
