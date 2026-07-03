### Title
`BridgedETHToL1ViaNativeBridge` event overstates L1-credited amount by `minimumFee` — (`contracts/bridges/LineaMessenger.sol`)

### Summary
`LineaMessenger.sendETHToL1ViaBridge` forwards the full `value` as `msg.value` to the Linea bridge but passes `minimumFee` as the `_fee` parameter. Per Linea's bridge semantics, the L1 recipient is credited `msg.value − _fee`, not `msg.value`. The calling pool contracts emit `BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees)` using the pre-fee amount, so the event always overstates what actually arrives on L1 by exactly `minimumFee`.

### Finding Description

**Call chain:**

1. `RSETHPool.bridgeAssetsViaNativeBridge()` (and identical copies in `RSETHPoolV2`, `RSETHPoolV3ExternalBridge`, `RSETHPoolNoWrapper`) computes `ethBalanceMinusFees` and calls: [1](#0-0) 

2. `LineaMessenger.sendETHToL1ViaBridge` receives `value = ethBalanceMinusFees`, fetches `minimumFee`, checks `value > minimumFee`, then calls: [2](#0-1) 

3. Linea's `sendMessage` credits `msg.value − _fee` to `_to` on L1. With `msg.value = value` and `_fee = minimumFee`, the L1Vault receives `value − minimumFee`.

4. Back in the pool, the event is emitted **before** any L1 confirmation and uses the pre-deduction figure: [3](#0-2) 

**Invariant broken:** `emitted amount = ethBalanceMinusFees`, but `L1 credited amount = ethBalanceMinusFees − minimumFee`. The gap equals `minimumFee` on every single bridge call.

**Extreme edge case (as posed):** If `ethBalanceMinusFees = minimumFee + 1 wei` (pool nearly empty), the guard `value > minimumFee` passes, 1 wei arrives on L1, but the event reports the full `minimumFee + 1 wei`. Off-chain systems reconciling the event against L1 receipts will see a near-total discrepancy.

### Impact Explanation
Off-chain accounting, dashboards, and any L1-side reconciliation logic that trusts `BridgedETHToL1ViaNativeBridge` will systematically overcount ETH arriving at the L1Vault by `minimumFee` per bridge call. No ETH is permanently lost (it is paid to the Linea postman as a legitimate relay fee), but the contract fails to deliver the amount it reports, matching the **Low — contract fails to deliver promised returns, but doesn't lose value** scope.

### Likelihood Explanation
This fires on **every** `bridgeAssetsViaNativeBridge()` call, not just the edge case. The `minimumFee` is a small but non-zero amount; the discrepancy is structural and unconditional. The BRIDGER_ROLE is a normal operational role, not an attacker.

### Recommendation
Emit the net amount that will be credited on L1:

```solidity
uint256 minimumFee = ILineaMessageService(l2bridge).minimumFeeInWei();
// ...
ILineaMessageService(l2bridge).sendMessage{ value: value }(target, minimumFee, bytes(""));
emit ETHSentViaLineaBridge(l2bridge, target, value - minimumFee, minimumFee);
```

And in the pool contracts, either:
- Pass the net amount to the event: `emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees - minimumFee)`, or
- Have `sendETHToL1ViaBridge` return the net credited amount so the pool can emit it accurately.

### Proof of Concept

```solidity
// MockLineaBridge: minimumFeeInWei() returns value - 1 (i.e., minimumFee = value - 1)
// value = ethBalanceMinusFees = 1000 wei, minimumFee = 999 wei

// LineaMessenger check: value (1000) > minimumFee (999) → passes
// sendMessage called with msg.value=1000, _fee=999
// L1 credited: 1000 - 999 = 1 wei

// Pool event: BridgedETHToL1ViaNativeBridge(l1Vault, 1000)
// Actual L1 receipt: 1 wei
// Discrepancy: 999 wei
```

A unit test deploying `LineaMessenger` with a mock bridge where `minimumFeeInWei()` returns `value - 1` will confirm the L1-credited amount is 1 wei while the emitted `ethBalanceMinusFees` equals `value`.

### Citations

**File:** contracts/pools/RSETHPool.sol (L487-493)
```text
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```

**File:** contracts/bridges/LineaMessenger.sol (L39-43)
```text
        uint256 minimumFee = ILineaMessageService(l2bridge).minimumFeeInWei();
        if (value <= minimumFee) revert InsufficientAmountForBridge(); // Ensure Linea native bridge fee can be covered
        // and there is some ETH actually bridged after deducting the fee

        ILineaMessageService(l2bridge).sendMessage{ value: value }(target, minimumFee, bytes(""));
```
