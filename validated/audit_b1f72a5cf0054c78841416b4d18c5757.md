Looking at the actual code flow for `bridgeAssetsViaNativeBridge()` and comparing it to `bridgeTokens()`.

### Title
Missing Zero-Amount Guard in `bridgeAssetsViaNativeBridge()` Allows 0-ETH Bridge Call and Misleading Event Emission - (File: `contracts/pools/RSETHPool.sol`)

---

### Summary

`bridgeAssetsViaNativeBridge()` does not check that `ethBalanceMinusFees > 0` before forwarding the amount to the messenger. A second call after the balance has already been drained succeeds silently, emitting a `BridgedETHToL1ViaNativeBridge` event with `ethBalanceMinusFees = 0` and causing off-chain accounting to record a phantom bridge transfer.

---

### Finding Description

`bridgeAssetsViaNativeBridge()` reads the bridgeable balance, forwards it to `ArbitrumMessenger.sendETHToL1ViaBridge`, and emits an event — with no guard against a zero amount: [1](#0-0) 

`getETHBalanceMinusFees()` is a pure balance read with no side-effects: [2](#0-1) 

`ArbitrumMessenger.sendETHToL1ViaBridge` only validates `msg.value == value`, which trivially holds when both are `0`: [3](#0-2) 

The `nonReentrant` modifier on `bridgeAssetsViaNativeBridge()` prevents reentrancy within a single transaction but offers no protection against two independent transactions in the same block. After tx1 drains the bridgeable ETH, tx2 computes `ethBalanceMinusFees = 0`, calls `sendETHToL1ViaBridge{value: 0}(...)` (which succeeds), and emits `BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, 0)`.

This is an inconsistency with `bridgeTokens()`, which explicitly reverts on zero balance: [4](#0-3) 

---

### Impact Explanation

The second call emits `BridgedETHToL1ViaNativeBridge` with `ethBalanceMinusFees = 0`. Any off-chain system (indexer, accounting dashboard, L1 reconciliation bot) that trusts this event will record a bridge transfer that moved no value. No ETH is lost, but the contract fails to deliver its promised behavior (a bridge call must transfer a positive amount), matching **Low — Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

Requires two `BRIDGER_ROLE` transactions to land in the same block. This can happen:
- Accidentally, when two independent BRIDGER_ROLE keyholders submit simultaneously.
- Through a scripting error that submits the call twice.

No malicious actor or key compromise is needed; it is an operational edge case with no on-chain protection.

---

### Recommendation

Add a zero-amount guard at the top of `bridgeAssetsViaNativeBridge()`, consistent with `bridgeTokens()`:

```solidity
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
if (ethBalanceMinusFees == 0) revert ZeroBridgeAmount();
```

---

### Proof of Concept

```solidity
// 1. Deploy RSETHPool with BRIDGER_ROLE granted to address(this).
// 2. Fund the pool with 1 ETH (no fees accrued, so feeEarnedInETH = 0).
// 3. Call bridgeAssetsViaNativeBridge() — tx1.
//    → getETHBalanceMinusFees() = 1 ETH; mock bridge receives 1 ETH.
//    → Event: BridgedETHToL1ViaNativeBridge(vault, 1 ETH).
// 4. Call bridgeAssetsViaNativeBridge() again — tx2 (same block).
//    → getETHBalanceMinusFees() = 0; mock bridge receives 0 ETH.
//    → Event: BridgedETHToL1ViaNativeBridge(vault, 0 ETH).  ← misleading
// 5. Assert: second event amount == 0 AND mock bridge balance unchanged after tx2.
```

The second call does not revert, emits the event with `0`, and the bridge contract receives nothing — demonstrating the missing guard.

### Citations

**File:** contracts/pools/RSETHPool.sol (L387-389)
```text
    function getETHBalanceMinusFees() public view returns (uint256) {
        return address(this).balance - feeEarnedInETH;
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

**File:** contracts/pools/RSETHPool.sol (L556-560)
```text
        uint256 balance = getTokenBalanceMinusFees(token);

        if (balance == 0) {
            revert ZeroBridgeAmount();
        }
```

**File:** contracts/bridges/ArbitrumMessenger.sol (L21-24)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
    }
```
