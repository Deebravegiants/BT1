Audit Report

## Title
Permissionless `updateRSETHPrice()` Enables Deposit-Update-Withdraw Sandwich to Extract Value from rsETH Holders - (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

## Summary

`LRTOracle.updateRSETHPrice()` is callable by any unprivileged address. Because `LRTDepositPool.getRsETHAmountToMint()` divides by the stored `rsETHPrice` and `LRTWithdrawalManager.getExpectedAssetAmount()` multiplies by it, an attacker can deposit at a stale (lower) price, force the price upward via `updateRSETHPrice()`, and immediately initiate a withdrawal at the newly elevated price — locking in an `expectedAssetAmount` that exceeds the original deposit. The surplus is extracted from existing rsETH holders.

## Finding Description

**Root cause:** `rsETHPrice` is a lazily-updated storage variable. Both the mint ratio on deposit and the redemption ratio on withdrawal read it directly from storage, creating a window where the two reads can observe different values within a single atomic transaction.

**Code path:**

`updateRSETHPrice()` carries no access control beyond `whenNotPaused`: [1](#0-0) 

Deposit minting divides by the stored `rsETHPrice`: [2](#0-1) 

`_updateRsETHPrice()` recomputes price as `(totalETHInProtocol - fee) / rsethSupply`, where `totalETHInProtocol` now includes the attacker's freshly deposited assets and `rsethSupply` includes the inflated rsETH minted at the stale price: [3](#0-2) 

`getExpectedAssetAmount()` multiplies by the now-updated `rsETHPrice`: [4](#0-3) 

`expectedAssetAmount` is locked at initiation time and paid out at completion: [5](#0-4) 

**Mathematical proof of profit:**

Let `P_s` = stale stored price, `P_t` = true price (`P_t > P_s`), `T` = total ETH in protocol, `S` = rsETH supply, `V` = ETH value of deposit (`V = X * assetPrice`).

- rsETH minted at deposit: `V / P_s` (inflated vs fair `V / P_t`)
- After deposit: `totalETH = T + V`, `rsethSupply = S + V/P_s`
- Price after `updateRSETHPrice()`: `P_new = (T + V) / (S + V/P_s)`
- Since `T > P_s * S` (because `P_t = T/S > P_s`), it follows that `P_new > P_s`
- Attacker's `expectedAssetAmount` = `(V/P_s) * P_new / assetPrice = X * (P_new / P_s) > X`
- **Profit per attack** = `X * (P_new/P_s - 1)`, funded by diluting existing holders

**Why the `pricePercentageLimit` guard is insufficient:**

The guard at line 256–266 only fires when `newRsETHPrice > highestRsethPrice` AND the increase exceeds the configured limit: [6](#0-5) 

Three bypass conditions exist:
1. `pricePercentageLimit == 0` (unset) — the guard is entirely skipped.
2. The staleness gap is within the configured limit (e.g., limit = 1%, gap = 0.5%) — the guard passes.
3. `highestRsethPrice > rsETHPrice` (price previously decreased) — `newRsETHPrice <= highestRsethPrice` so the branch is never entered.

Furthermore, the attacker's deposit itself dilutes the price increase: `P_new` is strictly between `P_s` and `P_t`, so the observed increase is always smaller than the raw staleness gap, making the guard even less likely to trigger.

**`getAvailableAssetAmount` check:**

```solidity
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
``` [7](#0-6) 

After the attacker deposits `X`, `totalAssets` increases by `X`, so `availableAmount` increases by `X`. The attacker's `expectedAssetAmount = X * (P_new/P_s)`. The excess `X * (P_new/P_s - 1)` must be covered by pre-existing available assets. In any live protocol with meaningful TVL this condition is trivially satisfied.

**`instantWithdrawal` collapses the attack to a single transaction:**

`instantWithdrawal` reads `rsETHPrice` live at call time: [8](#0-7) 

When `isInstantWithdrawalEnabled[asset] == true`, the attacker executes deposit → `updateRSETHPrice()` → `instantWithdrawal()` atomically with no withdrawal delay.

## Impact Explanation

**Critical — Direct theft of user funds.** The attacker recovers more underlying assets than deposited. The surplus is not protocol yield; it is value extracted from existing rsETH holders whose pro-rata backing is diluted by the inflated rsETH mint. The loss is permanent and proportional to the staleness gap and deposit size. With `instantWithdrawal` enabled the attack is fully atomic and repeatable every block.

## Likelihood Explanation

`rsETHPrice` is not updated on every deposit or withdrawal; it requires an explicit call. Staking rewards accrue continuously, so the stored price is routinely stale between keeper updates. The staleness gap is computable off-chain from public on-chain data (EigenLayer balances, LST exchange rates). Any EOA or contract can call `updateRSETHPrice()`. No special privileges, leaked keys, or governance capture are required. The only precondition — a non-zero staleness gap — is a normal operating condition. Likelihood is **Medium-High** (requires monitoring for a stale window, which is always present between keeper calls).

## Recommendation

1. **Restrict `updateRSETHPrice()` to a privileged keeper role** (e.g., `onlyLRTManager` or a dedicated `KEEPER_ROLE`), removing the ability for arbitrary callers to time price updates mid-transaction.
2. **Alternatively, snapshot the price at the start of each user transaction.** Compute rsETH-to-asset conversion using a price read at the beginning of `depositAsset` / `initiateWithdrawal` and pass it through rather than re-reading `rsETHPrice` from storage at each call site.
3. **For `instantWithdrawal`**, use the price at the time of the original withdrawal request (if a prior request exists) rather than the live price at execution time, consistent with the locked `expectedAssetAmount` model used in the delayed path.
4. As a defense-in-depth measure, ensure `pricePercentageLimit` is always set to a non-zero value and is calibrated to the expected maximum inter-update reward accrual rate.

## Proof of Concept

**Concrete numeric example (delayed withdrawal path):**

- `P_s = 1.000e18` (stale stored price), `P_t = 1.010e18` (true price, 1% stale)
- Protocol: `T = 1000 ETH`, `S ≈ 990.099 rsETH`
- Attacker deposits `X = 100 stETH` (assetPrice = 1e18)
- rsETH minted = `100 * 1e18 / 1.000e18 = 100 rsETH` (fair would be ≈ 99.01)
- After deposit: `totalETH = 1100`, `rsethSupply ≈ 1090.099`
- `updateRSETHPrice()` → `P_new = 1100 / 1090.099 ≈ 1.00908e18`
- `expectedAssetAmount = 100 * 1.00908e18 / 1e18 ≈ 100.908 stETH`
- **Profit ≈ 0.908 stETH** extracted from existing holders per 100 stETH deposited

**Foundry test plan:**

```solidity
function testSandwichAttack() public {
    // Setup: deploy protocol with stale rsETHPrice (simulate by not calling updateRSETHPrice
    // after staking rewards accrue to NodeDelegator)
    
    uint256 depositAmount = 100e18;
    uint256 attackerBalanceBefore = stETH.balanceOf(attacker);
    
    vm.startPrank(attacker);
    
    // Step 1: deposit at stale price
    stETH.approve(address(depositPool), depositAmount);
    depositPool.depositAsset(address(stETH), depositAmount, 0, "");
    uint256 rsETHReceived = rsETH.balanceOf(attacker);
    
    // Step 2: force price update
    oracle.updateRSETHPrice();
    uint256 priceAfterUpdate = oracle.rsETHPrice();
    assertGt(priceAfterUpdate, stalePriceBefore);
    
    // Step 3: initiate withdrawal at higher price
    rsETH.approve(address(withdrawalManager), rsETHReceived);
    withdrawalManager.initiateWithdrawal(address(stETH), rsETHReceived, "");
    
    // Step 4: fast-forward past delay, unlock queue, complete withdrawal
    vm.roll(block.number + withdrawalDelayBlocks + 1);
    // operator calls unlockQueue(...)
    withdrawalManager.completeWithdrawal(address(stETH), "");
    
    uint256 attackerBalanceAfter = stETH.balanceOf(attacker);
    assertGt(attackerBalanceAfter, attackerBalanceBefore); // profit confirmed
    vm.stopPrank();
}
```

For the instant-withdrawal variant, replace steps 3–4 with a single `instantWithdrawal()` call immediately after `updateRSETHPrice()`, making the entire exploit atomic within one transaction.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L231-250)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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

**File:** contracts/LRTWithdrawalManager.sol (L228-228)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L592-593)
```text
        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
