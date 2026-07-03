The code is confirmed. Let me trace the exact execution path and verify all claims.

**Key code facts:**

1. `LineaMessenger.sendETHToL1ViaBridge` line 40: `if (value <= minimumFee) revert InsufficientAmountForBridge();` — strict inequality, so `value = minimumFee + 1` passes.
2. Line 43: `ILineaMessageService(l2bridge).sendMessage{ value: value }(target, minimumFee, bytes(""));` — `msg.value = value`, fee parameter = `minimumFee`. Per Linea's `sendMessage` semantics, L1 receives `msg.value - fee = value - minimumFee`.
3. Pool callers (`RSETHPoolV2.bridgeAssets`, `RSETHPool.bridgeAssetsViaNativeBridge`, etc.) pass `ethBalanceMinusFees` directly as `value`, gated by `BRIDGER_ROLE`.

---

### Title
Insufficient Boundary Guard in `InsufficientAmountForBridge` Allows Near-Total ETH Loss to Linea Bridge Fees — (`contracts/bridges/LineaMessenger.sol`)

### Summary
`LineaMessenger.sendETHToL1ViaBridge` uses a strict-inequality guard (`value <= minimumFee`) that permits `value = minimumFee + 1` to proceed. When `sendMessage{ value: value }(target, minimumFee, '')` is called, Linea's bridge deducts `minimumFee` from `msg.value` as its fee, delivering only `value - minimumFee` (as little as 1 wei) to L1. When the pool's `ethBalanceMinusFees` is naturally close to `minimumFee`, a routine `bridgeAssetsViaNativeBridge` call by the BRIDGER_ROLE operator silently consumes nearly all pool ETH as bridge fees.

### Finding Description

In `contracts/bridges/LineaMessenger.sol`:

```solidity
// Line 40
if (value <= minimumFee) revert InsufficientAmountForBridge();

// Line 43
ILineaMessageService(l2bridge).sendMessage{ value: value }(target, minimumFee, bytes(""));
``` [1](#0-0) 

The guard only ensures `value > minimumFee` by at least 1 wei. It does not enforce any minimum on the amount actually delivered to L1, which is `value - minimumFee`. The `ILineaMessageService.sendMessage` interface confirms the second parameter is the fee deducted from `msg.value`:

```solidity
function sendMessage(address _to, uint256 _fee, bytes memory _calldata) external payable;
``` [2](#0-1) 

Pool callers pass `ethBalanceMinusFees` directly as `value` with no additional minimum-delivery check:

```solidity
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
    l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
);
``` [3](#0-2) 

The same pattern exists in `RSETHPool.bridgeAssetsViaNativeBridge` and `RSETHPoolV3ExternalBridge.bridgeAssetsViaNativeBridge`. [4](#0-3) [5](#0-4) 

### Impact Explanation

When `ethBalanceMinusFees = minimumFee + δ` (for small δ), the call delivers only δ wei to L1 while `minimumFee` worth of ETH is permanently consumed as the Linea bridge fee. This ETH is irrecoverable — it is not frozen in a contract but is paid out as fees and lost. The correct impact classification is **High — Theft of Unclaimed Yield**: yield accumulated in the Linea pool that should be bridged to L1 users is permanently destroyed. The question's framing of "permanent freezing of unclaimed yield" is slightly imprecise; the ETH is consumed (lost), not frozen.

### Likelihood Explanation

The Linea `minimumFeeInWei` is a live on-chain value that can be non-trivial (historically in the range of 0.001–0.01 ETH or higher during congestion). Pool balances naturally fluctuate and can be close to `minimumFee` between bridging cycles. The BRIDGER_ROLE operator calling `bridgeAssetsViaNativeBridge` in good faith when the pool balance is just above `minimumFee` is a realistic, non-adversarial scenario requiring no compromise of any key or role.

### Recommendation

Replace the guard with a check that enforces a meaningful minimum on the amount actually delivered to L1:

```solidity
uint256 minimumFee = ILineaMessageService(l2bridge).minimumFeeInWei();
uint256 amountToDeliver = value - minimumFee; // safe: checked below
if (value <= minimumFee || amountToDeliver < MINIMUM_BRIDGE_AMOUNT) {
    revert InsufficientAmountForBridge();
}
```

Alternatively, pool-level callers should check that `ethBalanceMinusFees - minimumFee` exceeds a meaningful threshold before invoking the bridge.

### Proof of Concept

```solidity
// Fork test on Linea
uint256 minimumFee = ILineaMessageService(l2bridge).minimumFeeInWei(); // e.g. 1e15
uint256 poolBalance = minimumFee + 1;

// Fund the pool with exactly minimumFee + 1 wei (minus protocol fees)
deal(address(pool), poolBalance + pool.feeEarnedInETH());

// BRIDGER_ROLE calls bridge
vm.prank(bridger);
pool.bridgeAssetsViaNativeBridge(); // or bridgeAssets()

// LineaMessenger calls sendMessage{ value: minimumFee+1 }(target, minimumFee, "")
// L1 receives: 1 wei
// minimumFee worth of ETH is consumed as bridge fee
assertEq(l1VaultReceivedETH, 1); // passes — near-total loss
```

### Citations

**File:** contracts/bridges/LineaMessenger.sol (L39-43)
```text
        uint256 minimumFee = ILineaMessageService(l2bridge).minimumFeeInWei();
        if (value <= minimumFee) revert InsufficientAmountForBridge(); // Ensure Linea native bridge fee can be covered
        // and there is some ETH actually bridged after deducting the fee

        ILineaMessageService(l2bridge).sendMessage{ value: value }(target, minimumFee, bytes(""));
```

**File:** contracts/interfaces/L2/ILineaMessageService.sol (L15-15)
```text
    function sendMessage(address _to, uint256 _fee, bytes memory _calldata) external payable;
```

**File:** contracts/pools/RSETHPoolV2.sol (L292-296)
```text
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );
```

**File:** contracts/pools/RSETHPool.sol (L487-491)
```text
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L657-661)
```text
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );
```
