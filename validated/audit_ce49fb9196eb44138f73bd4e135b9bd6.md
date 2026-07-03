The code is fully read. I have everything needed to evaluate this.

**Analysis of the exact code path:**

**Step 1 — Price update revert for non-managers:**
In `_updateRsETHPrice()`, when `newRsETHPrice > highestRsethPrice` and the increase exceeds `pricePercentageLimit`, non-manager callers hit a hard revert: [1](#0-0) 

The stored `rsETHPrice` is **not updated** — it stays at the pre-checkpoint stale value.

**Step 2 — Deposit uses the stale stored price:**
`getRsETHAmountToMint` reads `lrtOracle.rsETHPrice()` (the stored state variable, not a freshly computed value): [2](#0-1) 

A stale (lower) `rsETHPrice` means the denominator is smaller → attacker receives **more rsETH per unit of asset deposited** than they should.

**Step 3 — No staleness guard on deposits:**
`_beforeDeposit` has no check for oracle freshness or price staleness: [3](#0-2) 

**Step 4 — Manager path bypasses the revert:**
`updateRSETHPriceAsManager()` calls the same `_updateRsETHPrice()` but the role check at line 263 passes, so the price is updated to the correct higher value: [4](#0-3) 

The attack window is the gap between checkpoint finalization and the manager's call to `updateRSETHPriceAsManager`. This window is not bounded by any on-chain mechanism.

**Conclusion: This is a real, concrete vulnerability.**

---

### Title
Stale rsETH Price After Threshold-Blocked Update Enables Yield Theft via Deposit at Undervalued Rate — (`contracts/LRTOracle.sol`)

### Summary
When a large EigenLayer checkpoint finalization causes the computed rsETH price to exceed `highestRsethPrice` by more than `pricePercentageLimit`, `updateRSETHPrice()` reverts for non-manager callers, leaving `rsETHPrice` stale at the pre-checkpoint value. Any user can then deposit assets and receive more rsETH than the true exchange rate warrants. When the manager eventually calls `updateRSETHPriceAsManager()`, the attacker's rsETH is immediately worth more than what they deposited, at the expense of existing holders whose yield was diluted.

### Finding Description
`LRTOracle._updateRsETHPrice()` contains a safety guard that reverts with `PriceAboveDailyThreshold` when the newly computed price exceeds `highestRsethPrice` by more than `pricePercentageLimit` and the caller lacks the `MANAGER` role. The revert occurs **before** `rsETHPrice` is written, so the stored price remains at its previous (lower) value.

`LRTDepositPool.getRsETHAmountToMint()` computes the rsETH to mint as:

```
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

With a stale, artificially low `rsETHPrice` in the denominator, this division yields a larger-than-correct rsETH amount. There is no staleness check in `_beforeDeposit` and no pause triggered by the upward price breach (only downward breaches trigger a pause). The deposit pool remains open.

The attack window is entirely on-chain and permissionless: it lasts from the moment the checkpoint is finalized until the manager calls `updateRSETHPriceAsManager()`. This window can span multiple blocks or longer depending on manager response time.

### Impact Explanation
Existing rsETH holders bear the cost. When the attacker deposits at the stale lower price, they receive excess rsETH. After the manager updates the price upward, the total rsETH supply is now larger relative to TVL than it should be, meaning each pre-existing rsETH token represents a slightly smaller share of TVL. The yield that the checkpoint represented — which should have accrued proportionally to existing holders — is partially captured by the attacker. This is a direct theft of unclaimed yield (High impact per scope).

### Likelihood Explanation
- EigenLayer checkpoints accumulate beacon-chain rewards over time. A checkpoint covering weeks of rewards on a large pod can easily produce a price jump exceeding a tight `pricePercentageLimit` (e.g., 1%).
- The attacker needs no special role, no front-running, and no collusion. They only need to observe the checkpoint finalization on-chain and submit a deposit before the manager acts.
- The manager response is off-chain and not time-bounded by any contract mechanism, making the window realistic and exploitable.

### Recommendation
1. **Emit an event and/or set a flag when the price update is blocked** so monitoring systems can react immediately.
2. **Pause deposits** (or at minimum block `getRsETHAmountToMint` from returning a value based on a stale price) when the oracle price is known to be stale due to a blocked update. A simple `priceUpdateBlocked` flag set on revert and cleared on successful update would suffice.
3. Alternatively, **use the freshly computed price** (not the stored `rsETHPrice`) inside `getRsETHAmountToMint` so that even if the stored price is stale, deposits are priced at the current TVL-derived rate.

### Proof of Concept
```solidity
// Fork test outline (Foundry, mainnet fork post-checkpoint)
function testStaleYieldTheft() external {
    // 1. Simulate large beacon-chain yield: checkpoint finalized, TVL up >pricePercentageLimit
    //    (e.g., mock getEffectivePodShares to return a value 2% higher than before)

    // 2. Non-manager calls updateRSETHPrice() — expect revert
    vm.expectRevert(ILRTOracle.PriceAboveDailyThreshold.selector);
    lrtOracle.updateRSETHPrice();

    // 3. Record stale price
    uint256 stalePrice = lrtOracle.rsETHPrice();

    // 4. Attacker deposits ETH at stale price
    vm.deal(attacker, 10 ether);
    vm.prank(attacker);
    lrtDepositPool.depositETH{value: 10 ether}(0, "");
    uint256 attackerRsETH = rsETH.balanceOf(attacker);

    // 5. Manager updates price to correct value
    vm.prank(manager);
    lrtOracle.updateRSETHPriceAsManager();
    uint256 correctPrice = lrtOracle.rsETHPrice();
    assert(correctPrice > stalePrice);

    // 6. Assert attacker's rsETH is worth more than 10 ETH
    uint256 attackerETHValue = attackerRsETH * correctPrice / 1e18;
    assertGt(attackerETHValue, 10 ether);
}
```

### Citations

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L260-265)
```text
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-669)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
