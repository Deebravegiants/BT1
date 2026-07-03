### Title
Hardcoded `gasLimit=0` in `ScrollMessenger.sendETHToL1ViaBridge` Causes L1 Relay Failure and Temporary ETH Freeze - (File: `contracts/bridges/ScrollMessenger.sol`)

---

### Summary

`ScrollMessenger.sendETHToL1ViaBridge` passes a hardcoded `gasLimit=0` to Scroll's L2 messenger. The developer comment claims this "uses the default gas limit," but Scroll's protocol has no such concept — `gasLimit` is the literal gas forwarded to the target on L1. With `gasLimit=0`, the L1 relay call fails, and the bridged ETH is temporarily frozen in the Scroll L1 messenger until a replay is manually triggered.

---

### Finding Description

In `contracts/bridges/ScrollMessenger.sol` line 23:

```solidity
IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", 0, msg.sender);
//                                                                         ^
//                                                              gasLimit hardcoded to 0
``` [1](#0-0) 

The NatSpec comment on line 19 states `@dev Gas limit is set to 0 to use the default gas limit`, but the `IScrollMessenger` interface itself documents the parameter as:

> `@param gasLimit Gas limit required to complete the message relay on corresponding chain.` [2](#0-1) 

Scroll's L2 messenger accepts `gasLimit=0` without reverting (fee calculation yields ~0), so the L2 transaction succeeds and the message is queued. On L1, Scroll's `L1ScrollMessenger.relayMessageWithProof` executes:

```
target.call{value: value, gas: 0}("")
```

Even with the EVM's 2300-gas value-transfer stipend, any L1 vault contract with a non-trivial `receive()` (e.g., one that emits events or writes storage) will run out of gas. The relay emits `FailedRelayedMessage` and the ETH remains locked in the L1 messenger.

**Contrast with every other messenger in the codebase**, all of which hardcode `DEFAULT_GAS_LIMIT = 200_000`: [3](#0-2) [4](#0-3) 

The trigger path flows through all pool variants that call `bridgeAssetsViaNativeBridge()`: [5](#0-4) [6](#0-5) [7](#0-6) 

---

### Impact Explanation

Every legitimate `bridgeAssetsViaNativeBridge()` call on a Scroll-configured pool sends the entire `ethBalanceMinusFees` to L1 with `gasLimit=0`. The L1 relay fails, and the ETH is frozen in Scroll's L1 messenger until the BRIDGER_ROLE manually calls `replayMessage` on L2 with a corrected gas limit and pays the relay fee again. This is **temporary freezing of funds** (Medium).

---

### Likelihood Explanation

The bug is triggered by every normal invocation of `bridgeAssetsViaNativeBridge()` when the pool's `messenger` is set to `ScrollMessenger`. No attacker action is required — the BRIDGER_ROLE operator triggers it unintentionally during routine bridging operations. Likelihood is **high** for any Scroll-deployed pool.

---

### Recommendation

Replace the hardcoded `0` with a constant gas limit matching the other messenger contracts:

```solidity
uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
    if (msg.value != value) revert MismatchedMsgValue();
    IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", DEFAULT_GAS_LIMIT, msg.sender);
}
```

The `msg.value` forwarded must also cover the cross-domain fee (`gasLimit * gasPrice`) charged by Scroll's L2 message queue. Verify the fee is included or separately paid.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork test on Scroll L2 (or local fork)
// 1. Deploy ScrollMessenger
// 2. Call sendETHToL1ViaBridge{value: 1 ether}(scrollL2Messenger, l1Vault, 1 ether)
// 3. Observe SentMessage event with gasLimit=0
// 4. On L1 fork: call L1ScrollMessenger.relayMessageWithProof(...)
// 5. Assert: FailedRelayedMessage event is emitted (not RelayedMessage)
// 6. Assert: l1Vault.balance == 0 (ETH not delivered)
// 7. Assert: L1ScrollMessenger holds the 1 ether (frozen)

function testScrollGasLimitZeroFreezesETH() public {
    ScrollMessenger sm = new ScrollMessenger();
    vm.deal(address(this), 1 ether);

    // L2: message queued with gasLimit=0 — succeeds on L2
    sm.sendETHToL1ViaBridge{value: 1 ether}(SCROLL_L2_MESSENGER, L1_VAULT, 1 ether);

    // L1 fork: relay the message
    // Expected: FailedRelayedMessage emitted, ETH frozen in L1ScrollMessenger
    vm.selectFork(l1Fork);
    vm.expectEmit(true, false, false, false, SCROLL_L1_MESSENGER);
    emit FailedRelayedMessage(messageHash);
    IL1ScrollMessenger(SCROLL_L1_MESSENGER).relayMessageWithProof(...);

    assertEq(L1_VAULT.balance, 0);
    assertEq(SCROLL_L1_MESSENGER.balance, 1 ether);
}
```

### Citations

**File:** contracts/bridges/ScrollMessenger.sol (L19-24)
```text
     * @dev Gas limit is set to 0 to use the default gas limit
     */
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IScrollMessenger(l2bridge).sendMessage{ value: value }(target, value, "", 0, msg.sender);
    }
```

**File:** contracts/interfaces/L2/IScrollMessenger.sol (L62-63)
```text
    /// @param gasLimit Gas limit required to complete the message relay on corresponding chain.
    function sendMessage(address target, uint256 value, bytes calldata message, uint256 gasLimit) external payable;
```

**File:** contracts/bridges/OptimismMessenger.sol (L15-16)
```text
    /// @notice The recommended gas limit for sending ETH to L1 via the Optimism bridge
    uint32 public constant DEFAULT_GAS_LIMIT = 200_000;
```

**File:** contracts/bridges/BaseMessenger.sol (L14-15)
```text
    /// @notice The recommended gas limit for sending ETH to L1 via the Base bridge
    uint32 public constant DEFAULT_GAS_LIMIT = 200_000;
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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L466-480)
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
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L651-664)
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
