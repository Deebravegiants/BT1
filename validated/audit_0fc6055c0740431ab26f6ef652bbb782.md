Audit Report

## Title
Stale `rsETHPrice` Enables Deposit-Before-Update / Withdraw-After-Update Sandwich to Extract Yield from Existing Holders - (File: contracts/LRTOracle.sol, contracts/LRTDepositPool.sol, contracts/LRTWithdrawalManager.sol)

## Summary

`LRTOracle.rsETHPrice` is a mutable stored value that is never refreshed inside the deposit or withdrawal-initiation flows. Because `updateRSETHPrice()` is a public, permissionless function, an attacker can deposit at a stale-low price to receive excess rsETH, trigger the price update to the true higher value, and immediately initiate a withdrawal that locks in the inflated payout — extracting yield that belongs to pre-existing holders.

## Finding Description

`LRTOracle` stores the exchange rate in a mutable state variable: [1](#0-0) 

It is updated only when `updateRSETHPrice()` is called explicitly, which is `public` and `whenNotPaused` — callable by any unprivileged address: [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` divides by the stored (potentially stale) `rsETHPrice`: [3](#0-2) 

Neither `depositETH` nor `depositAsset` calls `updateRSETHPrice()` before computing the mint amount: [4](#0-3) 

`LRTWithdrawalManager.initiateWithdrawal()` similarly reads the stored price via `getExpectedAssetAmount` to lock in `expectedAssetAmount`: [5](#0-4) [6](#0-5) 

At unlock time, `_calculatePayoutAmount` returns the **minimum** of the locked `expectedAssetAmount` and the current return — meaning the amount locked at initiation is a ceiling, not a floor: [7](#0-6) 

The `pricePercentageLimit` guard in `_updateRsETHPrice()` blocks unprivileged callers only when the price jump exceeds the configured threshold: [8](#0-7) 

This guard limits the per-update exploitable gap but does not eliminate it. Staking rewards accrue continuously; any gap within the configured limit remains fully exploitable. If `pricePercentageLimit == 0`, the guard is entirely disabled and arbitrarily large stale gaps are exploitable.

**Exploit path:**
1. Observe that `rsETHPrice` is stale-low (rewards have accrued since last update, but the gap is within `pricePercentageLimit`).
2. Call `depositETH{value: X}(0, "")` — mints excess rsETH at the stale price.
3. Call `LRTOracle.updateRSETHPrice()` — updates `rsETHPrice` to the true higher value.
4. Call `initiateWithdrawal(asset, rsETHAmount, "")` — locks `expectedAssetAmount` using the now-updated higher price.
5. After `withdrawalDelayBlocks` (~8 days), call `completeWithdrawal(asset, "")` — receives the inflated payout.

**Numerical example (within a 1% `pricePercentageLimit`):**
- State: `totalETH = 1000`, `rsethSupply = 1000`, `rsETHPrice = 1.0` (stale; true rate = 1.005 due to 0.5% reward accrual).
- Attacker deposits 100 ETH → mints `100 / 1.0 = 100 rsETH` (correct: `100 / 1.005 ≈ 99.5 rsETH`).
- After deposit: `totalETH = 1105`, `rsethSupply = 1100`.
- Attacker calls `updateRSETHPrice()` → new price ≈ `1105 / 1100 ≈ 1.00455`.
- Attacker calls `initiateWithdrawal` with 100 rsETH → `expectedAssetAmount ≈ 100 × 1.00455 = 100.455 ETH`.
- After 8 days, attacker receives ≈ 100.455 ETH — a profit of ≈ 0.455 ETH at the expense of the 1000 original holders.

## Impact Explanation

**High — Theft of unclaimed yield.**

When staking rewards accrue, the true ETH-per-rsETH ratio rises above the stored `rsETHPrice`. An attacker who deposits before the price update receives more rsETH than the protocol's actual exchange rate warrants, diluting every existing holder. After triggering the price update, the attacker initiates a withdrawal at the now-correct (higher) price, locking in a payout that exceeds their original deposit. The difference is extracted from the yield that should have accrued to pre-existing holders. This matches the allowed impact class "Theft of unclaimed yield."

## Likelihood Explanation

**Medium.** Stale prices are the normal state between oracle updates; the protocol does not auto-update on every block. `updateRSETHPrice()` is public and costs only gas. The attacker needs no special role, no flash loan, and no MEV infrastructure — only the ability to sequence three transactions. The 8-day withdrawal delay does not prevent the attack; it only defers the payout (and introduces price-drop risk, but not price-rise risk since `expectedAssetAmount` is a ceiling). The `pricePercentageLimit` guard limits per-update price jumps but does not eliminate the window: rewards accumulate continuously, and even a sub-1% stale gap on a large deposit is profitable. If `pricePercentageLimit` is set to 0, the guard is entirely disabled.

## Recommendation

Refresh `rsETHPrice` at the **start** of every deposit and withdrawal-initiation call by invoking `_updateRsETHPrice()` internally before computing mint or payout amounts. Specifically:

- In `LRTDepositPool._beforeDeposit()`, call `ILRTOracle(lrtOracleAddress).updateRSETHPrice()` before reading `rsETHPrice`.
- In `LRTWithdrawalManager.initiateWithdrawal()`, call `ILRTOracle(...).updateRSETHPrice()` before calling `getExpectedAssetAmount()`.

This ensures the price used for minting and for locking withdrawal amounts always reflects the current state of the protocol, eliminating the stale-price window.

## Proof of Concept

**Minimal Foundry fork test outline:**

```solidity
function testSandwichYieldExtraction() public {
    // Setup: simulate reward accrual so true price > stored rsETHPrice
    // (e.g., send ETH rewards to DepositPool without minting rsETH)
    vm.deal(address(lrtDepositPool), address(lrtDepositPool).balance + rewardAmount);

    uint256 stalePriceBefore = lrtOracle.rsETHPrice();
    // stalePriceBefore < true price

    // Step 1: Deposit at stale price
    vm.prank(attacker);
    lrtDepositPool.depositETH{value: depositAmount}(0, "");
    uint256 rsETHReceived = rsETH.balanceOf(attacker);
    // Assert rsETHReceived > depositAmount / truePrice (excess minted)

    // Step 2: Update price
    vm.prank(attacker);
    lrtOracle.updateRSETHPrice();
    uint256 newPrice = lrtOracle.rsETHPrice();
    assertGt(newPrice, stalePriceBefore);

    // Step 3: Initiate withdrawal at updated price
    vm.prank(attacker);
    rsETH.approve(address(lrtWithdrawalManager), rsETHReceived);
    vm.prank(attacker);
    lrtWithdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHReceived, "");

    // Step 4: Advance blocks past withdrawal delay
    vm.roll(block.number + withdrawalDelayBlocks + 1);

    // Operator unlocks queue
    vm.prank(operator);
    lrtWithdrawalManager.unlockQueue(ETH_TOKEN, type(uint256).max, 0, type(uint256).max, 0, type(uint256).max);

    // Step 5: Complete withdrawal
    uint256 balanceBefore = attacker.balance;
    vm.prank(attacker);
    lrtWithdrawalManager.completeWithdrawal(ETH_TOKEN, "");
    uint256 profit = attacker.balance - balanceBefore - depositAmount;

    assertGt(profit, 0, "Attacker extracted yield from existing holders");
}
```

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTWithdrawalManager.sol (L168-173)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L832-834)
```text
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```
