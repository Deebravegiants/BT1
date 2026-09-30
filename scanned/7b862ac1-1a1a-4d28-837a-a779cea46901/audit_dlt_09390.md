# [?] Merge pull request #61 from bcnmy/2023-03-16-Reentrancy-Guard-Custom

## Summary
Severity: Unknown
Chain: Biconomy
Component: bcnmy/scw-contracts
Published: 2023-03-16
Source: https://github.com/bcnmy/scw-contracts/commit/5371d86e73fb0d7b4916008f042a83c5e3332dd7
Type: security-commit

## Details
Merge pull request #61 from bcnmy/2023-03-16-Reentrancy-Guard-Custom

Custom Reentrancy Guard + update to GuardManager test cases

## Patch
### contracts/smart-contract-wallet/SmartAccount.sol
```diff
@@ -7,10 +7,11 @@ import {FallbackManager} from "./base/FallbackManager.sol";
 import {SignatureDecoder} from "./common/SignatureDecoder.sol";
 import {SecuredTokenTransfer} from "./common/SecuredTokenTransfer.sol";
 import {LibAddress} from "./libs/LibAddress.sol";
+import {ISignatureValidator, ISignatureValidatorConstants} from "./interfaces/ISignatureValidator.sol";
 import {Math} from "./libs/Math.sol";
 import {IERC165} from "./interfaces/IERC165.sol";
+import {ReentrancyGuard} from "./common/ReentrancyGuard.sol";
 import {SmartAccountErrors} from "./common/Errors.sol";
-import {ISignatureValidator, ISignatureValidatorConstants} from "./interfaces/ISignatureValidator.sol";
 import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
 import {IModule} from "./test/IModule.sol";
 
@@ -22,13 +23,13 @@ contract SmartAccount is
     SecuredTokenTransfer,
     ISignatureValidatorConstants,
     IERC165,
+    ReentrancyGuard,
     SmartAccountErrors
 {
     using ECDSA for bytes32;
     using LibAddress for address;
 
     // Storage
-
     // Version
     string public constant VERSION = "1.0.4"; // using AA 0.4.0
 
@@ -245,7 +246,7 @@ contract SmartAccount is
         Transaction memory _tx,
         FeeRefund memory refundInfo,
         bytes memory signatures
-    ) public payable virtual returns (bool success) {
+    ) public payable virtual nonReentrant returns (bool success) {
         uint256 startGas = gasleft();
         bytes32 txHash;
         // Use scope here to limit variable lifetime and prevent `stack too deep` errors
```

### contracts/smart-contract-wallet/common/ReentrancyGuard.sol
```diff
@@ -0,0 +1,27 @@
+// SPDX-License-Identifier: LGPL-3.0-only
+pragma solidity 0.8.17;
+
+/// @title Reentrancy Guard - reentrancy protection
+abstract contract ReentrancyGuard {
+    error ReentrancyProtectionActivated();
+
+    uint256 private constant NOT_ENTERED = 1;
+    uint256 private constant ENTERED = 2;
+
+    uint256 private reentrancyStatus;
+
+    constructor() {
+        reentrancyStatus = NOT_ENTERED;
+    }
+
+    modifier nonReentrant() {
+        if (reentrancyStatus == ENTERED) revert ReentrancyProtectionActivated();
+        reentrancyStatus = ENTERED;
+        _;
+        reentrancyStatus = NOT_ENTERED;
+    }
+
+    function _isReentrancyGuardEntered() internal view returns (bool) {
+        return reentrancyStatus == ENTERED;
+    }
+}
```

### contracts/smart-contract-wallet/libs/SmartAccountStorage.sol
```diff
@@ -11,6 +11,8 @@ contract SmartAccountStorage {
 
     uint256[24] private __fallbackManagerGap;
 
+    uint256 private reentrancyStatus;
+
     // Smart Account Storage
     address internal owner;
 
```

### contracts/smart-contract-wallet/test/TestIncreaseNonceLib.sol
```diff
@@ -0,0 +1,15 @@
+// SPDX-License-Identifier: LGPL-3.0-only
+pragma solidity ^0.8.0;
+
+import "../libs/SmartAccountStorage.sol";
+import "../SmartAccount.sol";
+
+/// @title TestIncreaseNonceLib - Test Lib to Increase Nonce
+/// @notice used to test delegatecalls from Smart Account
+contract TestIncreaseNonceLib is SmartAccountStorage {
+    event NonceIncreasedFromLib(uint256 batchId, uint256 newNonce);
+
+    function increaseNonce(uint256 batchId) external {
+        emit NonceIncreasedFromLib(batchId, ++nonces[batchId]);
+    }
+}
```

### contracts/smart-contract-wallet/test/upgrades/Guards/DelegateCallTransactionGuard.sol
```diff
@@ -0,0 +1,36 @@
+// SPDX-License-Identifier: LGPL-3.0-only
+pragma solidity 0.8.17;
+
+import {Enum} from "../../../common/Enum.sol";
+import {BaseGuard} from "./GuardManager.sol";
+import {Transaction, FeeRefund} from "../../../BaseSmartAccount.sol";
+
+contract DelegateCallTransactionGuard is BaseGuard {
+    error DelegateCallGuardRestricted();
+
+    address public immutable allowedTarget;
+
+    constructor(address target) {
+        allowedTarget = target;
+    }
+
+    // solhint-disable-next-line payable-fallback
+    fallback() external {
+        // We don't revert on fallback to avoid issues in case of a SmartAccount upgrade
+        // E.g. The expected check method might change and then the Smart Account would be locked.
+    }
+
+    function checkTransaction(
+        Transaction memory _tx,
+        FeeRefund memory,
+        bytes memory,
+        address
+    ) external view override {
+        if (
+            _tx.operation == Enum.Operation.DelegateCall &&
+            _tx.to != allowedTarget
+        ) revert DelegateCallGuardRestricted();
+    }
+
+    function checkAfterExecution(bytes32, bool) external view override {}
+}
```

### contracts/smart-contract-wallet/test/upgrades/Guards/GuardManager.sol
```diff
@@ -0,0 +1,61 @@
+// SPDX-License-Identifier: LGPL-3.0-only
+pragma solidity 0.8.17;
+
+import {Enum} from "../../../common/Enum.sol";
+import {Transaction, FeeRefund} from "../../../BaseSmartAccount.sol";
+import {SelfAuthorized} from "../../../common/SelfAuthorized.sol";
+import {IERC165} from "../../../interfaces/IERC165.sol";
+
+interface Guard is IERC165 {
+    function checkTransaction(
+        Transaction memory _tx,
+        FeeRefund memory refundInfo,
+        bytes memory signatures,
+        address msgSender
+    ) external;
+
+    function checkAfterExecution(bytes32 txHash, bool success) external;
+}
+
+abstract contract BaseGuard is Guard {
+    function supportsInterface(
+        bytes4 interfaceId
+    ) external view virtual override returns (bool) {
+        return
+            interfaceId == type(Guard).interfaceId || // 0xe6d7a83a
+            interfaceId == type(IERC165).interfaceId; // 0x01ffc9a7
+    }
+}
+
+/// @title Guard Manager - A contract that manages transaction guards which perform pre and post-checks on execution by multisig owners
+/// @author Inspired by Richard Meissner's <richard@gnosis.pm> implementation
+contract GuardManager is SelfAuthorized {
+    event GuardChanged(address guard);
+    error InvalidGuard(address guard);
+    // keccak256("guard_manager.guard.address")
+    bytes32 internal constant GUARD_STORAGE_SLOT =
+        0x4a204f620c8c5ccdca3fd54d003badd85ba500436a431f0cbda4f558c93c34c8;
+
+    /// @dev Set a guard that checks transactions before execution
+    /// @param guard The address of the guard to be used or the 0 address to disable the guard
+    function setGuard(address guard) external authorized {
+        if (guard != address(0)) {
+            if (!Guard(guard).supportsInterface(type(Guard).interfaceId))
+                revert InvalidGuard(guard);
+        }
+        bytes32 slot = GUARD_STORAGE_SLOT;
+        // solhint-disable-next-line no-inline-assembly
+        assembly {
+            sstore(slot, guard)
+        }
+        emit GuardChanged(guard);
+    }
+
+    function getGuard() public view returns (address guard) {
+        bytes32 slot = GUARD_STORAGE_SLOT;
+        // solhint-disable-next-line no-inline-assembly
+        assembly {
+            guard := sload(slot)
+        }
+    }
+}
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount10.sol
```diff
@@ -7,6 +7,7 @@ import "../../base/ModuleManager.sol";
 import "../../base/FallbackManager.sol";
 import "../../common/SignatureDecoder.sol";
 import "../../common/SecuredTokenTransfer.sol";
+import {ReentrancyGuard} from "../../common/ReentrancyGuard.sol";
 import {SmartAccountErrors} from "../../common/Errors.sol";
 import "../../interfaces/ISignatureValidator.sol";
 import "../../interfaces/IERC165.sol";
@@ -19,6 +20,7 @@ contract SmartAccount10 is
     FallbackManager,
     SignatureDecoder,
     SecuredTokenTransfer,
+    ReentrancyGuard,
     ISignatureValidatorConstants,
     IERC165,
     SmartAccountErrors
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount11.sol
```diff
@@ -7,6 +7,7 @@ import "../../base/ModuleManager.sol";
 import "../../base/FallbackManager.sol";
 import "../../common/SignatureDecoder.sol";
 import "../../common/SecuredTokenTransfer.sol";
+import {ReentrancyGuard} from "../../common/ReentrancyGuard.sol";
 import {SmartAccountErrors} from "../../common/Errors.sol";
 import "../../interfaces/ISignatureValidator.sol";
 import "../../interfaces/IERC165.sol";
@@ -19,6 +20,7 @@ contract SmartAccount11 is
     FallbackManager,
     SignatureDecoder,
     SecuredTokenTransfer,
+    ReentrancyGuard,
     ISignatureValidatorConstants,
     IERC165,
     SmartAccountErrors
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount12Guard.sol
```diff
@@ -0,0 +1,139 @@
+// SPDX-License-Identifier: MIT
+pragma solidity 0.8.17;
+
+import "../../SmartAccount.sol";
+import {GuardManager, Guard} from "./Guards/GuardManager.sol";
+import "hardhat/console.sol";
+
+contract SmartAccount12Guard is SmartAccount, GuardManager {
+    constructor(IEntryPoint anEntryPoint) SmartAccount(anEntryPoint) {}
+
+    function execTransaction_S6W(
+        Transaction memory _tx,
+        FeeRefund memory refundInfo,
+        bytes memory signatures
+    ) public payable virtual override nonReentrant returns (bool success) {
+        uint256 startGas = gasleft();
+        bytes32 txHash;
+        // Use scope here to limit variable lifetime and prevent `stack too deep` errors
+        {
+            bytes memory txHashData = encodeTransactionData(
+                // Transaction info
+                _tx,
+                // Payment info
+                refundInfo,
+                // Signature info
+                nonces[1]++
+            );
+            txHash = keccak256(txHashData);
+            checkSignatures(txHash, signatures);
+        }
+
+        address guard = getGuard();
+        {
+            if (guard != address(0)) {
+                Guard(guard).checkTransaction(
+                    _tx,
+                    refundInfo,
+                    signatures,
+                    msg.sender
+                );
+            }
+        }
+
+        // We require some gas to emit the events (at least 2500) after the execution and some to perform code until the execution (500)
+        // We also include the 1/64 in the check that is not send along with a call to counteract potential shortings because of EIP-150
+        // Bitshift left 6 bits means multiplying by 64, just more gas efficient
+        if (
+            gasleft() <
+            Math.max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) + 500
+        )
+            revert NotEnoughGasLeft(
+                gasleft(),
+                Math.max((_tx.targetTxGas << 6) / 63, _tx.targetTxGas + 2500) +
+                    500
+            );
+        // Use scope here to limit variable lifetime and prevent `stack too deep` errors
+        {
+            // If the gasPrice is 0 we assume that nearly all available gas can be used (it is always more than targetTxGas)
+            // We only substract 2500 (compared to the 3000 before) to ensure that the amount passed is still higher than targetTxGas
+            success = execute(
+                _tx.to,
+                _tx.value,
+                _tx.data,
+                _tx.operation,
+                refundInfo.gasPrice == 0 ? (gasleft() - 2500) : _tx.targetTxGas
+            );
+            // If no targetTxGas and no gasPrice was set (e.g. both are 0), then the internal tx is required to be successful
+            // This makes it possible to use `estimateGas` without issues, as it searches for the minimum gas where the tx doesn't revert
+            if (!success && _tx.targetTxGas == 0 && refundInfo.gasPrice == 0)
+                revert CanNotEstimateGas(
+                    _tx.targetTxGas,
+                    refundInfo.gasPrice,
+                    success
+                );
+            // We transfer the calculated tx costs to the tx.origin to avoid sending it to intermediate contracts that have made calls
+            uint256 payment;
+            if (refundInfo.gasPrice != 0) {
+                payment = handlePaymentV12(
+                    startGas - gasleft(),
+                    refundInfo.baseGas,
+                    refundInfo.gasPrice,
+                    refundInfo.tokenGasPriceFactor,
+                    refundInfo.gasToken,
+                    refundInfo.refundReceiver
+                );
+                emit AccountHandlePayment(txHash, payment);
+            }
+        }
+        {
+            if (guard != address(0)) {
+                Guard(guard).checkAfterExecution(txHash, success);
+            }
+        }
+    }
+
+    /**
+     * @dev Handles the payment for a transaction refund from Smart Account to Relayer.
+     * @param gasUsed Gas used by the transaction.
+     * @param baseGas Gas costs that are independent of the transaction execution
+     * (e.g. base transaction fee, signature check, payment of the refund, emitted events).
+     * @param gasPrice Gas price / TokenGasPrice (gas price in the context of token using offchain price feeds)
+     * that should be used for the payment calculation.
+     * @param tokenGasPriceFactor factor by which calculated token gas price is already multiplied.
+     * @param gasToken Token address (or 0 if ETH) that is used for the payment.
+     * @return payment The amount of payment made in the specified token.
+     */
+    function handlePaymentV12(
+        uint256 gasUsed,
+        uint256 baseGas,
+        uint256 gasPrice,
+        uint256 tokenGasPriceFactor,
+        address gasToken,
+        address payable refundReceiver
+    ) private returns (uint256 payment) {
+        require(tokenGasPriceFactor != 0, "invalid tokenGasPriceFactor");
+        // solhint-disable-next-line avoid-tx-origin
+        address payable receiver = refundReceiver == address(0)
+            ? payable(tx.origin)
+            : refundReceiver;
+        if (gasToken == address(0)) {
+            // For ETH we will only adjust the gas price to not be higher than the actual used gas price
+            payment =
+                (gasUsed + baseGas) *
+                (gasPrice < tx.gasprice ? gasPrice : tx.gasprice);
+            bool success;
+            assembly {
+                success := call(gas(), receiver, payment, 0, 0, 0, 0)
+            }
+            if (!success)
+                revert TokenTransferFailed(address(0), receiver, payment);
+        } else {
+            payment =
+                ((gasUsed + baseGas) * (gasPrice)) /
+                (tokenGasPriceFactor);
+            if (!transferToken(gasToken, receiver, payment))
+                revert TokenTransferFailed(gasToken, receiver, payment);
+        }
+    }
+}
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount3.sol
```diff
@@ -7,6 +7,7 @@ import "../../base/ModuleManager.sol";
 import "../../base/FallbackManager.sol";
 import "../../common/SignatureDecoder.sol";
 import "../../common/SecuredTokenTransfer.sol";
+import {ReentrancyGuard} from "../../common/ReentrancyGuard.sol";
 import {SmartAccountErrors} from "../../common/Errors.sol";
 import "../../interfaces/ISignatureValidator.sol";
 import "../../interfaces/IERC165.sol";
@@ -18,6 +19,7 @@ contract SmartAccount3 is
     FallbackManager,
     SignatureDecoder,
     SecuredTokenTransfer,
+    ReentrancyGuard,
     ISignatureValidatorConstants,
     IERC165,
     SmartAccountErrors
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount4.sol
```diff
@@ -7,6 +7,7 @@ import "../../base/ModuleManager.sol";
 import "../../base/FallbackManager.sol";
 import "../../common/SignatureDecoder.sol";
 import "../../common/SecuredTokenTransfer.sol";
+import {ReentrancyGuard} from "../../common/ReentrancyGuard.sol";
 import {SmartAccountErrors} from "../../common/Errors.sol";
 import "../../interfaces/ISignatureValidator.sol";
 import "../../interfaces/IERC165.sol";
@@ -19,6 +20,7 @@ contract SmartAccount4 is
     FallbackManager,
     SignatureDecoder,
     SecuredTokenTransfer,
+    ReentrancyGuard,
     ISignatureValidatorConstants,
     IERC165,
     SmartAccountErrors
```

### contracts/smart-contract-wallet/test/upgrades/SmartAccount5.sol
```diff
@@ -7,6 +7,7 @@ import "../../base/ModuleManager.sol";
 import "../../base/FallbackManager.sol";
 import "../../common/SignatureDecoder.sol";
 import "../../common/SecuredTokenTransfer.sol";
+import {ReentrancyGuard} from "../../common/ReentrancyGuard.sol";
 import {SmartAccountErrors} from "../../common/Errors.sol";
 import "../../interfaces/ISignatureValidator.sol";
 import "../../interfaces/IERC165.sol";
@@ -19,6 +20,7 @@ contract SmartAccount5 is
     FallbackManager,
     SignatureDecoder,
     SecuredTokenTransfer,
+    ReentrancyGuard,
     ISignatureValidatorConstants,
     IERC165,
     SmartAccountErrors
```
