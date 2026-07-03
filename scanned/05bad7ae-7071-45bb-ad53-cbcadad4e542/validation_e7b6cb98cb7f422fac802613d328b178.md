Looking at the full call chain to determine if zero-value calls actually succeed silently.

### Title
Missing Zero-Amount Guard in `bridgeAssetsViaNativeBridge` Allows Silent Zero-Value ArbSys Withdrawal Tickets — (`contracts/pools/RSETHPool.sol`)

---

### Summary

`RSETHPool.bridgeAssetsViaNativeBridge()` reads `ethBalanceMinusFees` from `getETHBalanceMinusFees()` and forwards it directly to `ArbitrumMessenger.sendETHToL1ViaBridge`, then to `IArbitrumMessenger(l2bridge).withdrawEth{value: 0}`. When the pool holds no bridgeable ETH, the entire call chain completes without reverting, registering a zero-value withdrawal ticket on ArbSys and emitting a `BridgedETHToL1ViaNativeBridge` event with `amount = 0`. The `ZeroBridgeAmount` error is declared in the contract but never enforced in this function.

---

### Finding Description

The call chain on a zero-balance invocation is:

```
RSETHPool.bridgeAssetsViaNativeBridge()
  ethBalanceMinusFees = address(this).balance - feeEarnedInETH  // = 0
  IL2Messenger(messenger).sendETHToL1ViaBridge{value: 0}(l2Bridge, l1VaultETHForL2Chain, 0)
    ArbitrumMessenger.sendETHToL1ViaBridge(l2bridge, target, value=0)
      msg.value (0) != value (0)  → false → no revert
      IArbitrumMessenger(l2bridge).withdrawEth{value: 0}(target)
        ArbSys precompile: creates zero-value withdrawal ticket, does NOT revert
  emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, 0)
```

`ArbitrumMessenger.sendETHToL1ViaBridge` only guards against `msg.value != value`; when both are zero the check passes. [1](#0-0) 

Arbitrum's ArbSys precompile (`withdrawEth`) accepts zero-value calls and creates a withdrawal ticket without reverting, so the entire path succeeds silently.

`RSETHPool.bridgeAssetsViaNativeBridge()` performs no zero-amount check before forwarding: [2](#0-1) 

`getETHBalanceMinusFees()` legitimately returns 0 whenever the pool's ETH balance equals its accrued fees: [3](#0-2) 

The `ZeroBridgeAmount` error is declared in the same contract but is never used in `bridgeAssetsViaNativeBridge`: [4](#0-3) 

The same pattern exists in `RSETHPoolNoWrapper.bridgeAssetsViaNativeBridge()` and `RSETHPoolV3ExternalBridge.bridgeAssetsViaNativeBridge()`: [5](#0-4) [6](#0-5) 

Note: `RSETHPoolV2ExternalBridge.bridgeAssetsViaNativeBridge(uint256 amount)` takes an explicit amount and does enforce `if (amount == 0) revert InvalidAmount()`, showing the developers were aware of the need for this guard in parameterized variants but omitted it in the no-argument variants. [7](#0-6) 

---

### Impact Explanation

Any authorized `BRIDGER_ROLE` caller (including an automated keeper) can invoke `bridgeAssetsViaNativeBridge()` when the pool holds no bridgeable ETH. The result is:
- A zero-value ArbSys withdrawal ticket is registered on-chain, creating phantom accounting entries.
- The `BridgedETHToL1ViaNativeBridge` event is emitted with `amount = 0`, which off-chain indexers and monitoring systems may misinterpret as a successful bridge cycle.
- Gas is wasted on a no-op cross-chain operation.
- No ETH is lost; the invariant violated is that each bridge cycle must transfer a positive nonzero amount.

This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

The `BRIDGER_ROLE` is required, so an external attacker cannot trigger this directly. However, the realistic trigger is an automated keeper that calls `bridgeAssetsViaNativeBridge()` on a schedule or in response to the `BridgedETHToL1ViaNativeBridge` event (which carries no ticket ID to distinguish a completed bridge from a pending one). After the first successful bridge drains the pool, any subsequent scheduled call before new deposits arrive will silently succeed with `amount = 0`. This is a normal operational scenario, not an adversarial one.

---

### Recommendation

Add a zero-amount guard at the top of `bridgeAssetsViaNativeBridge()` in `RSETHPool.sol`, `RSETHPoolNoWrapper.sol`, and `RSETHPoolV3ExternalBridge.sol`, using the already-declared `ZeroBridgeAmount` error:

```solidity
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
if (ethBalanceMinusFees == 0) revert ZeroBridgeAmount();
```

Optionally, include the ArbSys withdrawal ticket ID (returned by `withdrawEth`) in the `BridgedETHToL1ViaNativeBridge` event to allow off-chain systems to unambiguously track each bridge cycle.

---

### Proof of Concept

```solidity
// Precondition: pool has been fully bridged, address(this).balance == feeEarnedInETH
// (e.g., balance = 0, feeEarnedInETH = 0)

// Call 1 (legitimate): bridges X ETH, emits BridgedETHToL1ViaNativeBridge(receiver, X)
pool.bridgeAssetsViaNativeBridge();

// Call 2 (zero-value, no revert):
// getETHBalanceMinusFees() == 0
// sendETHToL1ViaBridge{value:0}(...) → msg.value(0) == value(0) → no revert
// withdrawEth{value:0}(target) → ArbSys creates zero-value ticket, no revert
// emits BridgedETHToL1ViaNativeBridge(receiver, 0)
pool.bridgeAssetsViaNativeBridge(); // succeeds silently

// Assert: second call emitted amount=0 without reverting
// Assert: ArbSys registered a zero-value withdrawal ticket
```

### Citations

**File:** contracts/bridges/ArbitrumMessenger.sol (L21-24)
```text
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IArbitrumMessenger(l2bridge).withdrawEth{ value: value }(target);
    }
```

**File:** contracts/pools/RSETHPool.sol (L120-120)
```text
    error ZeroBridgeAmount();
```

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L431-444)
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
