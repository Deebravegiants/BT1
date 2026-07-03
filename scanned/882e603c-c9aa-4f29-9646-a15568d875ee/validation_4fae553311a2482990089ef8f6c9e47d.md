### Title
`rsETHPrice` and `highestRsethPrice` Unconditionally Reset to `1 ether` When `rsethSupply == 0`, Enabling First-Depositor Theft of Orphaned Protocol Rewards - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle._updateRsETHPrice()` unconditionally overwrites both `rsETHPrice` and `highestRsethPrice` to `1 ether` whenever `rsethSupply == 0`, discarding all previously accumulated price history. This is the direct analog of the reported H-27: a cumulative value is reset when a counter reaches zero, losing state that was legitimately earned. Any residual protocol assets present at that moment (e.g., EigenLayer staking rewards sitting in `NodeDelegator` contracts) become capturable by the first new depositor at the artificially deflated price.

---

### Finding Description

In `LRTOracle._updateRsETHPrice()`:

```solidity
if (rsethSupply == 0) {
    rsETHPrice = 1 ether;
    highestRsethPrice = 1 ether;
    return;
}
``` [1](#0-0) 

Both `rsETHPrice` and `highestRsethPrice` are overwritten with `1 ether` with no regard for the previous price. The function `updateRSETHPrice()` is public and callable by anyone when the contract is not paused: [2](#0-1) 

`rsethSupply` can legitimately reach zero through the normal withdrawal lifecycle. Users can burn rsETH via `instantWithdrawal` (which calls `IRSETH.burnFrom` directly) or via the standard `initiateWithdrawal` → `unlockQueue` path. Once the last rsETH is burned, any attacker can immediately call `updateRSETHPrice()` to trigger the reset.

At the moment of reset, `totalETHInProtocol` as computed by `_getTotalEthInProtocol()` may still be non-zero because it sums `assetStakedInEigenLayer + assetUnstakingFromEigenLayer` across all `NodeDelegator` contracts: [3](#0-2) 

EigenLayer staking rewards accrue continuously inside `NodeDelegator` contracts and are only moved to the deposit pool on operator action. These rewards are counted in `getTotalAssetDeposits` and therefore in `_getTotalEthInProtocol`, but they are not automatically distributed when rsETH supply drops to zero.

After the reset, `getRsETHAmountToMint` uses the deflated `rsETHPrice = 1 ether`: [4](#0-3) 

A new depositor therefore receives rsETH priced as if the protocol holds zero accumulated yield. On the next `updateRSETHPrice()` call, the price jumps to reflect the residual assets, and the new depositor captures the entire orphaned reward balance.

A secondary impact is that `highestRsethPrice` is also reset to `1 ether`. This value governs both the upside price-increase guard and the downside auto-pause: [5](#0-4) [6](#0-5) 

Resetting `highestRsethPrice` from, say, `1.05 ether` to `1 ether` means a price drop to `0.95 ether` (a ~9.5 % drop from the true peak) no longer triggers the auto-pause, weakening the downside protection for all subsequent depositors.

---

### Impact Explanation

**High — Theft of unclaimed yield.** Orphaned EigenLayer staking rewards that have accrued inside `NodeDelegator` contracts but have not yet been swept to the deposit pool are captured in full by the first depositor after the reset. The magnitude equals all rewards accumulated since the last operator sweep, which in a large deployment can be substantial. Additionally, the `highestRsethPrice` reset permanently weakens the price-deviation circuit-breaker for the new deposit epoch.

---

### Likelihood Explanation

`rsethSupply` reaching zero is a realistic edge case: it occurs naturally during a protocol migration, a coordinated mass-exit, or if `instantWithdrawal` is enabled and all holders exit. The public `updateRSETHPrice()` function means no privileged access is required to trigger the reset — any EOA can call it the moment supply hits zero. `pricePercentageLimit` is initialized to `0` by default (no explicit initialization in the contract), so the price-increase guard is disabled unless the admin has explicitly set it, making the single-block capture path viable.

---

### Recommendation

Preserve the last known price when `rsethSupply` drops to zero rather than resetting it:

```solidity
if (rsethSupply == 0) {
    // Do not reset rsETHPrice or highestRsethPrice.
    // The stored price remains valid for the next depositor.
    return;
}
```

If a deliberate reset to `1 ether` is desired (e.g., after a full protocol migration), it should be gated behind an explicit admin action rather than triggered automatically by a public function.

---

### Proof of Concept

1. Protocol has been running; `rsETHPrice = 1.05 ether`, `highestRsethPrice = 1.05 ether`. EigenLayer rewards of `R` ETH have accrued inside `NodeDelegator` contracts and are counted by `getEffectivePodShares()` / `getAssetBalance()`.
2. All rsETH holders exit via `instantWithdrawal` (or the standard queue). `rsethSupply → 0`. The `R` ETH rewards remain in the `NodeDelegator` and are still returned by `getTotalAssetDeposits`.
3. Attacker calls `updateRSETHPrice()`. Because `rsethSupply == 0`, `rsETHPrice = 1 ether` and `highestRsethPrice = 1 ether`.
4. Attacker calls `LRTDepositPool.depositETH{value: 1 ether}(0, "")`. `getRsETHAmountToMint` computes `(1e18 * 1e18) / 1e18 = 1 rsETH`. Attacker receives `1 rsETH`.
5. Attacker calls `updateRSETHPrice()` again. Now `rsethSupply = 1`, `totalETHInProtocol = 1 ETH (deposit) + R ETH (rewards)`. `rsETHPrice = (1 + R) * 1e18`.
6. Attacker calls `instantWithdrawal` (if enabled) or initiates a standard withdrawal. They receive `(1 + R)` ETH for `1 rsETH` deposited, stealing `R` ETH of orphaned staking rewards. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-222)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L252-257)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L270-274)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L330-348)
```text
    /// @return totalETHInProtocol total ETH in protocol (normalized to 1e18)
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L394-396)
```text
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
