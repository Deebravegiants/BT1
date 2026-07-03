### Title
Missing Zero-Address Validation on `target` in `ArbitrumMessenger.sendETHToL1ViaBridge` — (`contracts/bridges/ArbitrumMessenger.sol`)

---

### Summary

`ArbitrumMessenger.sendETHToL1ViaBridge` accepts an arbitrary `target` address with no zero-address guard. Any caller can pass `address(0)`, causing ETH to be permanently locked at the zero address on L1 via the Arbitrum native bridge.

---

### Finding Description

`ArbitrumMessenger.sendETHToL1ViaBridge` is a public, permissionless function with only one guard: `msg.value != value`. [1](#0-0) 

It passes `target` directly to `IArbitrumMessenger(l2bridge).withdrawEth{value: value}(target)` with no zero-address check. [2](#0-1) 

By contrast, `LineaMessenger.sendETHToL1ViaBridge` explicitly validates both `l2bridge` and `target`: [3](#0-2) 

The inconsistency is clear: the Linea variant was hardened; the Arbitrum variant was not.

---

### Impact Explanation

Any caller who invokes `ArbitrumMessenger.sendETHToL1ViaBridge(validBridge, address(0), value)` with `msg.value == value` will have their ETH registered as an L2→L1 withdrawal destined for `address(0)` on Ethereum mainnet. Once the Arbitrum challenge period elapses and the message is finalized, the ETH is claimable only by `address(0)` — permanently unrecoverable. The bridge contract does not revert; it silently accepts the zero-address destination.

Impact: **Low — Contract fails to deliver promised bridge return to the intended L1 recipient** (and in practice the ETH is permanently frozen, which could be argued as Critical for the affected caller's funds).

---

### Likelihood Explanation

The function is `external` with no role check, no pause gate, and no access restriction. Any EOA or contract can call it directly. The pool contracts that call it in production always validate `l1VaultETHForL2Chain` as non-zero before invoking: [4](#0-3) 

So the protocol's own bridging flow is safe. However, a direct caller (e.g., an integrator, a script, or a user interacting with the contract directly) can trigger the zero-address path without any on-chain protection.

---

### Recommendation

Add a zero-address check for both `l2bridge` and `target` at the top of `sendETHToL1ViaBridge`, mirroring the pattern already used in `LineaMessenger`:

```solidity
function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
+   UtilLib.checkNonZeroAddress(l2bridge);
+   UtilLib.checkNonZeroAddress(target);
    if (msg.value != value) revert MismatchedMsgValue();
    IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
}
```

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/bridges/ArbitrumMessenger.sol";

contract MockArbitrumBridge {
    address public lastDestination;
    function withdrawEth(address destination) external payable {
        lastDestination = destination;
    }
}

contract ArbitrumMessengerZeroAddressTest is Test {
    ArbitrumMessenger messenger;
    MockArbitrumBridge mockBridge;

    function setUp() public {
        messenger = new ArbitrumMessenger();
        mockBridge = new MockArbitrumBridge();
    }

    function test_zeroAddressTargetAccepted() public {
        vm.deal(address(this), 1 ether);
        // Call with address(0) as target — should revert but does NOT
        messenger.sendETHToL1ViaBridge{value: 1 ether}(
            address(mockBridge),
            address(0),   // zero address target
            1 ether
        );
        // ETH is now registered for delivery to address(0) on L1
        assertEq(mockBridge.lastDestination(), address(0));
    }
}
```

Running this test against unmodified code will pass (no revert), confirming `address(0)` is accepted as a valid L1 recipient.

### Citations

**File:** contracts/bridges/ArbitrumMessenger.sol (L21-24)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
    }
```

**File:** contracts/bridges/LineaMessenger.sol (L32-33)
```text
        UtilLib.checkNonZeroAddress(l2bridge);
        UtilLib.checkNonZeroAddress(target);
```

**File:** contracts/pools/RSETHPool.sol (L482-491)
```text
        UtilLib.checkNonZeroAddress(l2Bridge);
        UtilLib.checkNonZeroAddress(messenger);
        UtilLib.checkNonZeroAddress(l1VaultETHForL2Chain);

        // withdraw ETH - fees
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );
```
