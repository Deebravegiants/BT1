### Title
Zero-ETH Bridge Call Emits Misleading `BridgedETHToL1ViaNativeBridge` Event — (`contracts/pools/RSETHPool.sol`, `RSETHPoolNoWrapper.sol`, `RSETHPoolV3ExternalBridge.sol`)

---

### Summary

The no-argument `bridgeAssetsViaNativeBridge()` in `RSETHPool`, `RSETHPoolNoWrapper`, and `RSETHPoolV3ExternalBridge` contains no zero-amount guard. When `getETHBalanceMinusFees()` returns `0`, the function calls the messenger with `{value: 0}` and emits `BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, 0)`, falsely signalling a successful bridge of zero ETH to L1.

---

### Finding Description

`bridgeAssetsViaNativeBridge()` reads `ethBalanceMinusFees` from `getETHBalanceMinusFees()` and passes it directly to the messenger without checking for zero:

```solidity
// RSETHPool.sol:487-493
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
    l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
);
emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
``` [1](#0-0) [2](#0-1) [3](#0-2) 

`getETHBalanceMinusFees()` returns `address(this).balance - feeEarnedInETH`. When all pool ETH is accounted as fees (e.g., after many swaps at a high `feeBps` with no new deposits), this returns `0`. [4](#0-3) 

The messenger implementations (`ArbitrumMessenger`, `BaseMessenger`, `OptimismMessenger`, `ScrollMessenger`, `UnichainMessenger`) only check `msg.value != value`. When both are `0`, this check passes silently:

```solidity
// ArbitrumMessenger.sol:22-23
if (msg.value != value) revert MismatchedMsgValue();
IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target); // called with value=0
``` [5](#0-4) [6](#0-5) [7](#0-6) 

The `LineaMessenger` is the only messenger that independently guards against this with `if (value == 0) revert ZeroAmount()`, so Linea-based deployments are not affected. [8](#0-7) 

The fix is already present in `RSETHPoolV2ExternalBridge.bridgeAssetsViaNativeBridge(uint256 amount)`, which explicitly checks `if (amount == 0) revert InvalidAmount()`, demonstrating developer awareness of the pattern — but the no-arg variants were not updated. [9](#0-8) 

---

### Impact Explanation

A `BridgedETHToL1ViaNativeBridge` event is emitted with `amount = 0`. Off-chain accounting systems, dashboards, or L1 reconciliation logic that trust this event will record a bridge transfer that delivered nothing to `l1VaultETHForL2Chain`. No ETH is lost (fees remain in the pool), but the contract fails to deliver its promised behaviour (bridging available ETH to L1) and emits a misleading state-change event.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

The precondition (`feeEarnedInETH == address(this).balance`) is reachable in normal operation: a pool with a non-zero `feeBps` that has processed many swaps without any new ETH deposits can reach a state where all remaining ETH is fee-reserved. A `BRIDGER_ROLE` operator calling `bridgeAssetsViaNativeBridge()` at that moment triggers the issue without any malicious intent. The role is trusted but the contract should still enforce the invariant.

---

### Recommendation

Add a zero-amount guard at the top of the no-arg `bridgeAssetsViaNativeBridge()` in all three affected contracts, mirroring the pattern already used in `RSETHPoolV2ExternalBridge`:

```solidity
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
if (ethBalanceMinusFees == 0) revert InvalidAmount();
```

---

### Proof of Concept

```solidity
// Local unit test (no mainnet required)
function test_zeroBridgeEvent() public {
    // Setup: pool has 1 ETH, all of it is fee
    vm.deal(address(pool), 1 ether);
    // Simulate feeEarnedInETH == balance (e.g., via storage slot manipulation or
    // by calling deposit with feeBps=10000 so entire deposit becomes fee)
    stdstore.target(address(pool)).sig("feeEarnedInETH()").checked_write(1 ether);

    // getETHBalanceMinusFees() == 0
    assertEq(pool.getETHBalanceMinusFees(), 0);

    // BRIDGER_ROLE calls bridgeAssetsViaNativeBridge
    vm.prank(bridger);
    vm.expectEmit(true, false, false, true);
    emit BridgedETHToL1ViaNativeBridge(l1Vault, 0); // emitted with amount=0
    pool.bridgeAssetsViaNativeBridge();

    // L1Vault receives nothing; event was misleading
    assertEq(address(l1Vault).balance, 0);
}
```

### Citations

**File:** contracts/pools/RSETHPool.sol (L387-389)
```text
    function getETHBalanceMinusFees() public view returns (uint256) {
        return address(this).balance - feeEarnedInETH;
    }
```

**File:** contracts/pools/RSETHPool.sol (L487-493)
```text
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L437-443)
```text
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L657-663)
```text
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```

**File:** contracts/bridges/ArbitrumMessenger.sol (L21-24)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
    }
```

**File:** contracts/bridges/BaseMessenger.sol (L23-26)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IBaseMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
    }
```

**File:** contracts/bridges/OptimismMessenger.sol (L24-27)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IOptimismMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
    }
```

**File:** contracts/bridges/LineaMessenger.sol (L35-35)
```text
        if (value == 0) revert ZeroAmount();
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L471-471)
```text
        if (amount == 0) revert InvalidAmount();
```
