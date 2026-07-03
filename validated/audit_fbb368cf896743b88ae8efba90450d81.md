### Title
Missing Zero-Amount Guard in `bridgeAssetsViaNativeBridge()` Allows Silent 0-ETH Bridge Call with Misleading Event - (`contracts/pools/RSETHPool.sol`)

---

### Summary

`RSETHPool.bridgeAssetsViaNativeBridge()` does not check whether `ethBalanceMinusFees` is zero before forwarding the value to the messenger. A second call after all bridgeable ETH has already been sent succeeds silently, emits `BridgedETHToL1ViaNativeBridge` with `amount = 0`, and calls the Arbitrum bridge with 0 ETH.

---

### Finding Description

`bridgeAssetsViaNativeBridge()` computes the bridgeable amount as:

```solidity
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
// getETHBalanceMinusFees() = address(this).balance - feeEarnedInETH
``` [1](#0-0) 

After the first successful call, `address(this).balance` drops to exactly `feeEarnedInETH` (all non-fee ETH was sent out). A second call therefore computes `ethBalanceMinusFees = 0`. There is no guard against this: [2](#0-1) 

The call then reaches `ArbitrumMessenger.sendETHToL1ViaBridge` with `value = 0` and `msg.value = 0`: [3](#0-2) 

The only guard there is `msg.value != value`, which passes trivially when both are 0. The call to `withdrawEth{ value: 0 }` proceeds, and the event is emitted with 0 ETH.

By contrast, the sibling function `bridgeTokens()` correctly guards against this with an explicit zero check: [4](#0-3) 

The same missing guard exists in `RSETHPoolNoWrapper.bridgeAssetsViaNativeBridge()` and `RSETHPoolV3ExternalBridge.bridgeAssetsViaNativeBridge()`. [5](#0-4) [6](#0-5) 

---

### Impact Explanation

The second call:
- Does not revert
- Emits `BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, 0)` — a false record of a bridge operation
- Calls the Arbitrum bridge with 0 ETH, wasting gas and polluting on-chain/off-chain accounting

No funds are lost. Impact: **Low — contract fails to deliver promised returns (a meaningful bridge transfer), but doesn't lose value.**

---

### Likelihood Explanation

Requires `BRIDGER_ROLE`. The scenario is reachable via:
- An operator calling the function twice in sequence (e.g., a scripting error or a multicall batch)
- Two separate transactions in the same block

No adversarial actor is needed; this is an accidental operator path with no existing protection.

---

### Recommendation

Add a zero-amount guard at the top of `bridgeAssetsViaNativeBridge()`, consistent with `bridgeTokens()`:

```solidity
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
if (ethBalanceMinusFees == 0) revert ZeroBridgeAmount();
```

Apply the same fix to `RSETHPoolNoWrapper` and `RSETHPoolV3ExternalBridge`.

---

### Proof of Concept

```solidity
// 1. Pool has 1 ETH bridgeable balance (feeEarnedInETH = 0)
// 2. BRIDGER_ROLE calls bridgeAssetsViaNativeBridge() → tx1
//    ethBalanceMinusFees = 1 ETH → bridge receives 1 ETH → pool balance = 0
// 3. BRIDGER_ROLE calls bridgeAssetsViaNativeBridge() → tx2
//    ethBalanceMinusFees = 0 → bridge receives 0 ETH
//    BridgedETHToL1ViaNativeBridge emitted with amount = 0
// Assert: second event amount == 0, bridge received 0 ETH in tx2
```

### Citations

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
