Looking at the full contract and all callers, I can now make a definitive determination.

**Key facts from the code:**

`ArbitrumMessenger.sendETHToL1ViaBridge` has **no access control** and **no zero-value guard**: [1](#0-0) 

The only guard is `msg.value != value`, which passes trivially when both are `0`. [2](#0-1) 

All legitimate callers (e.g., `RSETHPool.bridgeAssetsViaNativeBridge`, `RSETHPoolV2.bridgeAssets`, `RSETHPoolV2ExternalBridge.bridgeAssetsViaNativeBridge`) are gated by `onlyRole(BRIDGER_ROLE)`, but `ArbitrumMessenger` itself is not: [3](#0-2) [4](#0-3) 

---

### Title
Missing zero-value guard in `sendETHToL1ViaBridge` allows unprivileged zero-ETH bridge calls — (`contracts/bridges/ArbitrumMessenger.sol`)

### Summary
`ArbitrumMessenger.sendETHToL1ViaBridge` has no access control and no check that `value > 0`. Any caller can invoke it with `value = 0` and `msg.value = 0`, satisfying the only guard (`msg.value != value`), and cause the Arbitrum bridge to register a zero-ETH L2→L1 message that delivers nothing to L1.

### Finding Description
The function signature is:

```solidity
function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value)
    external payable nonReentrant
{
    if (msg.value != value) revert MismatchedMsgValue();
    IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
}
```

There are two missing validations:
1. No role/access check — any EOA or contract can call it directly, bypassing the `BRIDGER_ROLE` gate that all pool callers enforce.
2. No `value > 0` check — the equality guard `msg.value != value` is satisfied when both are zero, so `withdrawEth{value: 0}(target)` is called and the transaction succeeds while bridging nothing.

### Impact Explanation
The contract's stated purpose (per NatSpec and interface) is to bridge ETH from L2 to L1. A successful call that registers a zero-ETH withdrawal violates the invariant that every successful `sendETHToL1ViaBridge` call results in a positive ETH amount being registered for L1 delivery. No principal is lost, matching the **Low** scope: *contract fails to deliver promised returns, but doesn't lose value*.

### Likelihood Explanation
The function is `external` with no access control. Any unprivileged address on Arbitrum can call it at any time with zero cost (beyond gas). The path is direct and requires no special setup.

### Recommendation
Add a zero-value guard at the top of the function:

```solidity
function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value)
    external payable nonReentrant
{
    if (value == 0) revert ZeroValueBridge();          // add this
    if (msg.value != value) revert MismatchedMsgValue();
    IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
}
```

Optionally, also add an access-control modifier (e.g., `onlyRole(BRIDGER_ROLE)`) consistent with all pool callers, to prevent arbitrary external invocation.

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/bridges/ArbitrumMessenger.sol";

contract MockL2Bridge {
    uint256 public lastValue;
    function withdrawEth(address) external payable {
        lastValue = msg.value;
    }
}

contract ArbitrumMessengerZeroValueTest is Test {
    ArbitrumMessenger messenger;
    MockL2Bridge mockBridge;
    address target = address(0xBEEF);

    function setUp() public {
        messenger = new ArbitrumMessenger();
        mockBridge = new MockL2Bridge();
    }

    function test_zeroValueCallSucceeds() public {
        // Unprivileged caller, value=0, msg.value=0
        messenger.sendETHToL1ViaBridge{value: 0}(address(mockBridge), target, 0);

        // Call succeeded but zero ETH was registered for L1 delivery
        assertEq(mockBridge.lastValue(), 0, "zero ETH registered — invariant violated");
    }
}
```

Running this test against unmodified code will pass, confirming the invariant is broken.

### Citations

**File:** contracts/bridges/ArbitrumMessenger.sol (L21-24)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
    }
```

**File:** contracts/pools/RSETHPool.sol (L481-494)
```text
    function bridgeAssetsViaNativeBridge() external nonReentrant onlyRole(BRIDGER_ROLE) {
        UtilLib.checkNonZeroAddress(l2Bridge);
        UtilLib.checkNonZeroAddress(messenger);
        UtilLib.checkNonZeroAddress(l1VaultETHForL2Chain);

        // withdraw ETH - fees
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L466-479)
```text
    function bridgeAssetsViaNativeBridge(uint256 amount) external nonReentrant onlyRole(BRIDGER_ROLE) {
        UtilLib.checkNonZeroAddress(l2Bridge);
        UtilLib.checkNonZeroAddress(messenger);
        UtilLib.checkNonZeroAddress(l1VaultETHForL2Chain);

        if (amount == 0) revert InvalidAmount();

        // bridge up to the ETH balance minus fees
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
        if (amount > ethBalanceMinusFees) revert InsufficientETHBalance();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: amount }(l2Bridge, l1VaultETHForL2Chain, amount);

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, amount);
```
