# [?] fix(solidity): add reentrancy guard to QuotedCalls.execute (#8493)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2026-04-01
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/f2749a66624b888df6e51413c77c822bc8594d8e
Type: security-commit

## Details
fix(solidity): add reentrancy guard to QuotedCalls.execute (#8493)

## Patch
### .changeset/reentrancy-guard-quotedcalls.md
```diff
@@ -0,0 +1,5 @@
+---
+'@hyperlane-xyz/core': minor
+---
+
+Added reentrancy guard using transient storage to QuotedCalls.execute and a corresponding test that verifies reentrant calls revert.
```

### solidity/contracts/libs/ReentrancyGuardTransient.sol
```diff
@@ -0,0 +1,39 @@
+// SPDX-License-Identifier: MIT OR Apache-2.0
+pragma solidity >=0.8.24;
+
+/*@@@@@@@       @@@@@@@@@
+ @@@@@@@@@       @@@@@@@@@
+  @@@@@@@@@       @@@@@@@@@
+   @@@@@@@@@       @@@@@@@@@
+    @@@@@@@@@@@@@@@@@@@@@@@@@
+     @@@@@  HYPERLANE  @@@@@@@
+    @@@@@@@@@@@@@@@@@@@@@@@@@
+   @@@@@@@@@       @@@@@@@@@
+  @@@@@@@@@       @@@@@@@@@
+ @@@@@@@@@       @@@@@@@@@
+@@@@@@@@@       @@@@@@@@*/
+
+import {TransientStorage} from "./TransientStorage.sol";
+
+/**
+ * @title ReentrancyGuardTransient
+ * @notice Reentrancy guard using EIP-1153 transient storage.
+ * @dev Drop-in replacement for OpenZeppelin's ReentrancyGuard that avoids
+ *      the cold SLOAD/SSTORE cost by using transient storage instead.
+ *      The guard is automatically cleared at the end of each transaction.
+ */
+abstract contract ReentrancyGuardTransient {
+    using TransientStorage for bytes32;
+
+    bytes32 private constant _REENTRANCY_SLOT =
+        keccak256("hyperlane.reentrancyGuard");
+
+    error ReentrancyGuardReentrantCall();
+
+    modifier nonReentrant() {
+        if (_REENTRANCY_SLOT.loadBool()) revert ReentrancyGuardReentrantCall();
+        _REENTRANCY_SLOT.set();
+        _;
+        _REENTRANCY_SLOT.clear();
+    }
+}
```

### solidity/contracts/token/QuotedCalls.sol
```diff
@@ -16,6 +16,7 @@ pragma solidity >=0.8.0;
 import {Address} from "@openzeppelin/contracts/utils/Address.sol";
 import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
+import {ReentrancyGuardTransient} from "../libs/ReentrancyGuardTransient.sol";
 import {IAllowanceTransfer} from "permit2/interfaces/IAllowanceTransfer.sol";
 
 import {IPostDispatchHook} from "../interfaces/hooks/IPostDispatchHook.sol";
@@ -164,7 +165,7 @@ library CalldataHeadLib {
  *      to the caller. Quote submitter = address(this) — only this contract
  *      can submit. The signer authorizes a specific user's quotes.
  */
-contract QuotedCalls is PackageVersioned {
+contract QuotedCalls is PackageVersioned, ReentrancyGuardTransient {
     using SafeERC20 for IERC20;
 
     // ============ Immutables ============
@@ -284,7 +285,7 @@ contract QuotedCalls is PackageVersioned {
     function execute(
         bytes calldata commands,
         bytes[] calldata inputs
-    ) external payable {
+    ) external payable nonReentrant {
         require(commands.length == inputs.length, "length mismatch");
 
         for (uint256 i; i < commands.length; ++i) {
```

### solidity/test/token/QuotedCalls.t.sol
```diff
@@ -29,6 +29,41 @@ import {InterchainAccountRouter} from "../../contracts/middleware/InterchainAcco
 import {CallLib} from "../../contracts/middleware/libs/Call.sol";
 import {Quote} from "../../contracts/interfaces/ITokenBridge.sol";
 import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
+import {ReentrancyGuardTransient} from "../../contracts/libs/ReentrancyGuardTransient.sol";
+
+/// @dev Contract that attempts reentrancy via the SWEEP ETH callback.
+contract ReentrantAttacker {
+    QuotedCalls target;
+    bool attacked;
+    bytes public reentrantRevertReason;
+
+    constructor(QuotedCalls _target) {
+        target = _target;
+    }
+
+    function attack() external payable {
+        // Execute a SWEEP that sends ETH to this contract, triggering receive()
+        bytes memory commands = hex"08"; // SWEEP
+        bytes[] memory inputs = new bytes[](1);
+        inputs[0] = abi.encode(address(0));
+        target.execute{value: msg.value}(commands, inputs);
+    }
+
+    receive() external payable {
+        if (!attacked) {
+            attacked = true;
+            // Re-enter execute during ETH sweep
+            bytes memory commands = hex"08"; // SWEEP
+            bytes[] memory inputs = new bytes[](1);
+            inputs[0] = abi.encode(address(0));
+            (bool success, bytes memory reason) = address(target).call(
+                abi.encodeCall(target.execute, (commands, inputs))
+            );
+            require(!success, "reentrancy should have reverted");
+            reentrantRevertReason = reason;
+        }
+    }
+}
 
 /// @dev Minimal mock Permit2. Skips signature verification; just sets allowances and transfers.
 ///      Tracks nonces and reverts on reuse, matching real Permit2 behavior.
@@ -1900,6 +1935,23 @@ contract QuotedCallsTest is Test {
             "no ETH stuck in QuotedCalls"
         );
     }
+    // ============ Tests: Reentrancy Guard ============
+
+    function test_execute_reentrancy_reverts() public {
+        ReentrantAttacker attacker = new ReentrantAttacker(quotedCalls);
+        vm.deal(address(attacker), 1 ether);
+
+        // The attacker's receive() catches the revert and stores the reason
+        attacker.attack{value: 1 ether}();
+
+        assertEq(
+            attacker.reentrantRevertReason(),
+            abi.encodeWithSelector(
+                ReentrancyGuardTransient.ReentrancyGuardReentrantCall.selector
+            )
+        );
+    }
+
     // Storage vars for fuzz test (avoids stack-too-deep)
     uint256 totalTokenNeeded;
     uint256 totalNativeNeeded;
```
