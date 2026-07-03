### Title
Pending withdrawal rsETH remains in `totalSupply()` causing yield theft from withdrawing users - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

When a user calls `initiateWithdrawal()`, their rsETH is transferred to `LRTWithdrawalManager` but **not burned**. The `expectedAssetAmount` is locked at the current rsETH price. During the mandatory pending period (default 8 days), the rsETH remains in `totalSupply()` and the corresponding protocol assets remain in `totalETHInProtocol`, so yield continues to accrue and the rsETH price rises. When `unlockQueue()` is finally called, `_calculatePayoutAmount` caps the user's payout at `min(expectedAssetAmount, currentReturn)` — always `expectedAssetAmount` when the price has risen. The yield that accrued on the pending withdrawal assets is silently redistributed to remaining rsETH holders, causing the withdrawing user to lose their rightful yield.

---

### Finding Description

**Step 1 — rsETH transferred but not burned at `initiateWithdrawal()`** [1](#0-0) 

The rsETH is moved to `LRTWithdrawalManager` via `safeTransferFrom`. It is **not** burned here. `expectedAssetAmount` is computed from the current oracle price and stored in the `WithdrawalRequest` struct. `assetsCommitted[asset]` is incremented to prevent double-counting for new withdrawal requests, but the assets themselves remain in the protocol's accounting.

**Step 2 — rsETH in `LRTWithdrawalManager` is counted in `totalSupply()` during price updates** [2](#0-1) [3](#0-2) 

`_updateRsETHPrice()` reads `IRSETH(rsETHTokenAddress).totalSupply()`, which includes the rsETH sitting in `LRTWithdrawalManager`. It also reads `_getTotalEthInProtocol()`, which sums balances across `LRTDepositPool`, all `NodeDelegator` contracts, EigenLayer strategies, and `LRTUnstakingVault` — all of which still hold the assets corresponding to the pending withdrawal. Both numerator and denominator include the pending withdrawal position, so the price ratio rises normally as yield accrues.

**Step 3 — Payout is capped at the original locked amount** [4](#0-3) 

`_calculatePayoutAmount` returns `min(expectedAssetAmount, currentReturn)`. When yield has accrued and the rsETH price has risen, `currentReturn > expectedAssetAmount`, so the user receives only `expectedAssetAmount` — the amount locked at initiation time. The rsETH is then burned at the higher price: [5](#0-4) 

The difference between `currentReturn` and `expectedAssetAmount` (the accrued yield) is never paid to the user. It remains in the protocol's asset pool and is effectively redistributed to all remaining rsETH holders.

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield.**

Every withdrawing user loses the yield that accrues on their rsETH during the pending period. With a default delay of 8 days and typical EigenLayer/LST staking yields (~4% APY), the loss per withdrawal is approximately `withdrawalAmount × 4% × (8/365) ≈ 0.088%`. For a 1,000 ETH withdrawal this is ~0.88 ETH. The lost yield is not destroyed — it is redistributed to remaining rsETH holders, constituting a direct transfer of value from withdrawing users to remaining holders.

---

### Likelihood Explanation

**Likelihood: High.**

This condition is triggered on every withdrawal where any yield accrues during the pending period. Since the protocol continuously earns EigenLayer restaking rewards and LST staking rewards, yield accrual during an 8-day window is the normal operating state, not an edge case. Any unprivileged user who calls `initiateWithdrawal()` is affected.

---

### Recommendation

Burn the rsETH immediately at `initiateWithdrawal()` instead of holding it in `LRTWithdrawalManager`. This removes the pending withdrawal rsETH from `totalSupply()` at the moment the `expectedAssetAmount` is locked, preventing the price from rising on behalf of the withdrawing user's share. The `assetsCommitted` accounting already prevents those assets from being double-allocated to new withdrawals, so burning the rsETH immediately is the correct symmetric action. Alternatively, exclude the rsETH balance held in `LRTWithdrawalManager` from `totalSupply()` in the oracle price calculation, though burning is simpler and more robust.

---

### Proof of Concept

1. Protocol state: rsETH price = 1.10 ETH/rsETH, total supply = 10,000 rsETH, total ETH = 11,000 ETH.
2. Alice calls `initiateWithdrawal(ETH, 1000e18, "")`.
   - 1,000 rsETH transferred to `LRTWithdrawalManager` (not burned).
   - `expectedAssetAmount = 1000 × 1.10 / 1.0 = 1,100 ETH` locked.
   - `assetsCommitted[ETH] += 1,100`.
3. 8 days pass. EigenLayer rewards accrue: total ETH in protocol rises to 11,110 ETH (1% yield).
4. `updateRSETHPrice()` is called:
   - `rsethSupply = 10,000` (Alice's 1,000 rsETH still in supply).
   - `totalETHInProtocol = 11,110`.
   - `newRsETHPrice = 11,110 / 10,000 = 1.111 ETH/rsETH`.
5. Operator calls `unlockQueue(ETH, ...)`:
   - `currentReturn = 1000 × 1.111 / 1.0 = 1,111 ETH`.
   - `payoutAmount = min(1,100, 1,111) = 1,100 ETH`.
   - 1,000 rsETH burned; 1,100 ETH redeemed from vault.
6. Alice calls `completeWithdrawal(ETH, "")` and receives 1,100 ETH.
7. **Alice loses 11 ETH of yield** (1,111 − 1,100) that accrued on her position during the 8-day pending period. This 11 ETH remains in the protocol and is redistributed to the remaining 9,000 rsETH holders. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-173)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L302-307)
```text
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );

        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
    }
```

**File:** contracts/LRTOracle.sol (L214-216)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();
```

**File:** contracts/LRTOracle.sol (L249-250)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```
