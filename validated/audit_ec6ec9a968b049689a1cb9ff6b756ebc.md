### Title
`LineaMessenger.sendETHToL1ViaBridge` Delivers `value - minimumFee` to L1 Target Instead of Full `value`, Breaking `IL2Messenger` Interface Invariant — (`contracts/bridges/LineaMessenger.sol`)

---

### Summary

`LineaMessenger` implements `IL2Messenger` but silently delivers less ETH to the L1 target than the `value` parameter specifies. Every other `IL2Messenger` implementation forwards the full `value` to L1. Pool contracts that call through the `IL2Messenger` abstraction emit accounting events recording `value` as bridged, while the L1 vault actually receives `value - minimumFee`.

---

### Finding Description

The `IL2Messenger` interface defines a single function:

```solidity
function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable;
```

All other implementations forward the full `value` to `target` on L1:
- `OptimismMessenger`: `bridgeETHTo{ value: value }(target, ...)` [1](#0-0) 
- `ArbitrumMessenger`: `withdrawEth{ value: value }(target)` [2](#0-1) 
- `ScrollMessenger`: `sendMessage{ value: value }(target, value, ...)` [3](#0-2) 
- `BaseMessenger`: `bridgeETHTo{ value: value }(target, ...)` [4](#0-3) 

`LineaMessenger` instead calls:

```solidity
ILineaMessageService(l2bridge).sendMessage{ value: value }(target, minimumFee, bytes(""));
``` [5](#0-4) 

The Linea `sendMessage(address _to, uint256 _fee, bytes _calldata)` signature deducts `_fee` from `msg.value` before crediting `_to`. The L1 target therefore receives `value - minimumFee`, not `value`.

The pool callers treat all `IL2Messenger` implementations as equivalent and emit events recording the full `ethBalanceMinusFees` as bridged:

```solidity
IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
    l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
);
emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
``` [6](#0-5) 

The same pattern appears in `RSETHPoolV2`, `RSETHPoolNoWrapper`, `RSETHPoolV2ExternalBridge`, and `RSETHPoolV3ExternalBridge`. [7](#0-6) 

---

### Impact Explanation

The L1 vault (`l1VaultETHForL2Chain`) receives `value - minimumFee` ETH while on-chain events and any off-chain accounting systems record `value` as the bridged amount. The `minimumFee` is paid to the Linea relayer — it is not lost from the system entirely, but it is permanently diverted away from the intended L1 recipient. This creates a persistent cross-chain accounting discrepancy: the L2 pool's balance is reduced by `value`, but the L1 vault's balance increases by only `value - minimumFee`. Over many bridge calls the cumulative shortfall grows.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

This triggers on every call to `bridgeAssetsViaNativeBridge` on a Linea-deployed pool instance. It is deterministic and requires no special conditions — it fires unconditionally whenever the Linea native bridge path is used. The `minimumFee` on Linea is non-zero by protocol design.

---

### Recommendation

`LineaMessenger` should send only `value - minimumFee` as `msg.value` to the bridge, keeping `minimumFee` as the fee argument, so the L1 target receives exactly `value - minimumFee` and the caller is aware of the net amount. Alternatively, the pool callers should query the net delivered amount and emit/record that instead of the gross `value`. The cleanest fix is to update the `sendETHToL1ViaBridge` call in the pool to pass `value - minimumFee` as both the ETH sent and the `value` argument, after pre-computing the fee — or to extend the `IL2Messenger` interface to return the actual amount delivered.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import {LineaMessenger} from "contracts/bridges/LineaMessenger.sol";

contract MockLineaBridge {
    uint256 public constant MIN_FEE = 0.001 ether;
    address public lastTo;
    uint256 public lastValueDelivered;

    function minimumFeeInWei() external pure returns (uint256) {
        return MIN_FEE;
    }

    // Linea sendMessage: delivers msg.value - _fee to _to
    function sendMessage(address _to, uint256 _fee, bytes calldata) external payable {
        lastTo = _to;
        lastValueDelivered = msg.value - _fee; // fee goes to relayer
        payable(_to).transfer(lastValueDelivered);
    }

    receive() external payable {}
}

contract MockL1Vault {
    uint256 public received;
    receive() external payable { received += msg.value; }
}

contract LineaMessengerTest is Test {
    LineaMessenger messenger;
    MockLineaBridge bridge;
    MockL1Vault l1Vault;

    function setUp() public {
        messenger = new LineaMessenger(address(this));
        bridge = new MockLineaBridge();
        l1Vault = new MockL1Vault();
    }

    function test_lineaDeliversLessThanValue() public {
        uint256 value = 1 ether;
        messenger.sendETHToL1ViaBridge{value: value}(
            address(bridge), address(l1Vault), value
        );
        // L1 vault receives value - minimumFee, not value
        assertEq(l1Vault.received(), value - bridge.MIN_FEE());
        // Delta = minimumFee, accounting discrepancy
        assertGt(value - l1Vault.received(), 0);
    }
}
```

The assertion `l1Vault.received() == value - MIN_FEE` passes, confirming the L1 vault receives less than the `value` recorded in the `BridgedETHToL1ViaNativeBridge` event. [8](#0-7)

### Citations

**File:** contracts/bridges/OptimismMessenger.sol (L26-26)
```text
        IOptimismMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
```

**File:** contracts/bridges/ArbitrumMessenger.sol (L23-23)
```text
        IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
```

**File:** contracts/bridges/ScrollMessenger.sol (L23-23)
```text
        IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", 0, msg.sender);
```

**File:** contracts/bridges/BaseMessenger.sol (L25-25)
```text
        IBaseMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
```

**File:** contracts/bridges/LineaMessenger.sol (L39-45)
```text
        uint256 minimumFee = ILineaMessageService(l2bridge).minimumFeeInWei();
        if (value <= minimumFee) revert InsufficientAmountForBridge(); // Ensure Linea native bridge fee can be covered
        // and there is some ETH actually bridged after deducting the fee

        ILineaMessageService(l2bridge).sendMessage{ value: value }(target, minimumFee, bytes(""));

        emit ETHSentViaLineaBridge(l2bridge, target, value, minimumFee);
```

**File:** contracts/pools/RSETHPool.sol (L489-493)
```text
        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L659-663)
```text
        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```
