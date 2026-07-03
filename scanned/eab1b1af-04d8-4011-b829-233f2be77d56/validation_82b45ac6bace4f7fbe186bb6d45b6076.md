### Title
Stale `rsETHPrice` in `LRTOracle` Allows Depositors to Mint Excess rsETH When `pricePercentageLimit` Blocks Public Updates — (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a stored state variable used as the denominator in rsETH minting. When the true rsETH price rises beyond `pricePercentageLimit`, public calls to `updateRSETHPrice()` revert, leaving the stored price stale. Any depositor can then call `LRTDepositPool.depositAsset` or `depositETH` and receive more rsETH than their deposit is worth, diluting existing holders.

---

### Finding Description

`LRTDepositPool.getRsETHAmountToMint` computes the rsETH to mint as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

`lrtOracle.rsETHPrice()` is a stored state variable in `LRTOracle` — it is **not** recomputed on every deposit. It is updated only when `updateRSETHPrice()` (or `updateRSETHPriceAsManager()`) is called.

Inside `_updateRsETHPrice()`, when the newly computed price exceeds `highestRsethPrice` by more than `pricePercentageLimit`, the function reverts for any caller who is not a manager:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

if (isPriceIncreaseOffLimit) {
    if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
        revert PriceAboveDailyThreshold();
    }
}
``` [2](#0-1) 

Because the revert occurs **before** `rsETHPrice = newRsETHPrice` is executed, the stored price is never updated: [3](#0-2) 

During the window between the price exceeding the limit and the manager manually calling `updateRSETHPriceAsManager()`, the stored `rsETHPrice` is **lower than the true price**. The minting formula divides by this stale low value, producing a larger-than-correct rsETH amount for every depositor.

The deposit entry points that trigger this path are: [4](#0-3) [5](#0-4) 

The `minRSETHAmountExpected` slippage guard only protects the depositor from receiving *too little* rsETH — it does not prevent over-minting: [6](#0-5) 

---

### Impact Explanation

When `rsETHPrice` is stale and lower than the true price, every depositor receives more rsETH than the ETH value they contributed. After the manager updates the price, the attacker's rsETH is redeemable for more ETH than was deposited. The profit is extracted directly from existing rsETH holders, whose proportional share of the TVL is diluted. This constitutes **theft of unclaimed yield** from existing holders (High severity).

---

### Likelihood Explanation

`pricePercentageLimit` is a live protocol parameter intended to be set conservatively (e.g., 1 % = `1e16`). Staking rewards accumulate continuously; if `updateRSETHPrice()` is not called frequently enough, the true price can exceed the limit by the time the next call is attempted. Any unprivileged depositor can exploit the window between the price exceeding the limit and the manager's manual intervention. No special permissions, front-running, or oracle manipulation are required — only a deposit transaction during the stale window.

---

### Recommendation

1. **Compute price on-the-fly**: Replace the stored `rsETHPrice` read in `getRsETHAmountToMint` with an inline TVL-over-supply calculation so the minting rate always reflects the current state.
2. **Atomic price update before deposit**: Call `_updateRsETHPrice()` (or a view equivalent) inside `_beforeDeposit` and revert if the price cannot be updated (i.e., if the increase exceeds the limit and the caller is not a manager).
3. **Raise or remove `pricePercentageLimit` for upward moves**: The limit is designed as a safety guard against manipulation, but blocking legitimate upward price updates creates the stale-price window. Consider applying the limit only to price *decreases* (which already trigger a pause), and allowing unrestricted upward updates.

---

### Proof of Concept

1. `pricePercentageLimit` is set to 1 % (`1e16`); `highestRsethPrice` = `1.00e18`.
2. Staking rewards accumulate; true rsETH price becomes `1.02e18` (2 % increase).
3. Any user calls `updateRSETHPrice()` → reverts with `PriceAboveDailyThreshold` because `0.02e18 > 0.01e18`.
4. Stored `rsETHPrice` remains `1.00e18`.
5. Attacker deposits 100 ETH via `depositETH(0, "")`.
6. `getRsETHAmountToMint` returns `100e18 * 1e18 / 1.00e18 = 100 rsETH` instead of the correct `100e18 / 1.02e18 ≈ 98.04 rsETH`.
7. Attacker receives ≈ 1.96 excess rsETH at no cost.
8. Manager calls `updateRSETHPriceAsManager()` → `rsETHPrice` updates to `1.02e18`.
9. Attacker's 100 rsETH is now redeemable for 102 ETH — a 2 ETH profit extracted from existing holders.

The root cause mirrors the external report exactly: a stale stored price (analogous to `shortOrder.price`) is used in a minting formula instead of the current oracle value, allowing a user to receive more tokens than their collateral/deposit is worth.

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
