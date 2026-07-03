Audit Report

## Title
Late Depositors Steal Yield from Existing rsETH Holders via Stale `rsETHPrice` - (`contracts/LRTOracle.sol`)

## Summary
`LRTDepositPool.getRsETHAmountToMint()` divides by the stored `rsETHPrice` state variable, which is only updated on explicit calls to `updateRSETHPrice()`. Between updates, any accrued rewards (MEV, LST appreciation, EigenLayer rewards) cause the protocol's real TVL to exceed `rsethSupply × rsETHPrice`, creating a window where a depositor receives more rsETH than their contribution warrants. When `_updateRsETHPrice()` is subsequently called, it computes `previousTVL` using the current (inflated) supply at the old price, silently absorbing the late depositor's shares into the baseline and diluting existing holders' yield.

## Finding Description
`getRsETHAmountToMint()` computes:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

`rsETHPrice` is a plain storage variable updated only by explicit calls to `updateRSETHPrice()` or `updateRSETHPriceAsManager()`. The deposit flow (`depositETH` / `depositAsset` → `_beforeDeposit` → `getRsETHAmountToMint`) never triggers a price refresh before minting. [2](#0-1) 

Inside `_updateRsETHPrice()`, the previous TVL baseline is:
```solidity
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
``` [3](#0-2) 

Here `rsethSupply` is `IRSETH(rsETHTokenAddress).totalSupply()` — the **current** supply already including any deposits made at the stale price. Multiplying this inflated supply by the old price overstates the baseline, making the `rewardAmount = totalETHInProtocol - previousTVL` appear the same as it would have been without the attacker's deposit, while the new price is computed over a larger denominator:
```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

The reward sources that create the stale-price window are all live and continuous: ETH balance in `LRTDepositPool` (MEV via `receiveFromRewardReceiver`), LST price appreciation via `getAssetPrice`, and EigenLayer pod shares via `getEffectivePodShares`. [5](#0-4) 

The `pricePercentageLimit` guard does not prevent the exploit: if the price increase is within the limit, any caller (including the attacker) can call `updateRSETHPrice()` immediately after depositing. If the increase exceeds the limit, the attacker's deposit at the stale price is already committed on-chain and the attacker still benefits when the manager eventually calls `updateRSETHPriceAsManager()`. [6](#0-5) 

## Impact Explanation
**High — Theft of unclaimed yield.**

Concrete trace (no protocol fee for clarity):

| Step | rsethSupply | totalETH | rsETHPrice |
|---|---|---|---|
| Initial | 100 | 100 ETH | 1.00 |
| Rewards accrue | 100 | 110 ETH | 1.00 (stale) |
| Attacker deposits 10 ETH | 110 | 120 ETH | 1.00 (stale) |
| `updateRSETHPrice()` called | 110 | 120 ETH | 120/110 ≈ **1.0909** |

- Attacker's 10 rsETH → worth **10.909 ETH** (gain of **0.909 ETH** from others' yield).
- Original 100 rsETH → worth **109.09 ETH** instead of **110 ETH** (loss of **0.91 ETH**).

Without the attacker the correct price would be 110/100 = **1.10**. The delta is a direct, concrete transfer of yield from existing holders to the attacker, matching the allowed impact "Theft of unclaimed yield."

## Likelihood Explanation
`updateRSETHPrice()` is a public, permissionless function callable by any EOA. Reward accrual is continuous (every block, LST prices tick upward; MEV arrives asynchronously). An attacker needs only to: (1) read `_getTotalEthInProtocol()` off-chain and compare to `rsethSupply × rsETHPrice` to detect a profitable gap, (2) call `depositETH()` or `depositAsset()`, (3) call `updateRSETHPrice()`. No privileged access, no victim interaction, and no special timing beyond waiting for rewards to accrue — a condition that is always eventually true. The attack is repeatable every keeper cycle.

## Recommendation
**Option A (preferred):** Call `_updateRsETHPrice()` at the start of `depositETH()` and `depositAsset()` before `_beforeDeposit()` computes `getRsETHAmountToMint()`. This ensures every depositor pays the fair price that already reflects all accrued rewards.

**Option B:** Snapshot `rsethSupply` at the time of the last price update (store it as `rsethSupplyAtLastUpdate`) and use that snapshot — not the current supply — when computing `previousTVL` inside `_updateRsETHPrice()`. This prevents new deposits made at the stale price from being absorbed into the baseline.

## Proof of Concept
```
1. Deploy protocol; 100 ETH deposited → 100 rsETH minted; rsETHPrice = 1.0.
2. 10 ETH of staking rewards flow into LRTDepositPool via FeeReceiver.sendFunds().
   totalETHInProtocol = 110 ETH; rsETHPrice still = 1.0 (not yet updated).
3. Attacker calls depositETH(10 ETH):
   getRsETHAmountToMint = (10e18 * 1e18) / 1e18 = 10 rsETH minted.
   rsethSupply = 110; totalETH = 120.
4. Attacker calls updateRSETHPrice():
   rsethSupply = 110 (current, includes attacker)
   previousTVL = 110 * 1.0 = 110 ETH
   rewardAmount = 120 - 110 = 10 ETH
   newRsETHPrice = 120 / 110 ≈ 1.0909
5. Attacker redeems 10 rsETH → receives ≈ 10.909 ETH (profit ≈ 0.909 ETH).
6. Original 100 rsETH holders collectively receive ≈ 109.09 ETH instead of 110 ETH.
   Loss to original holders: ≈ 0.91 ETH stolen by attacker.

Foundry test plan:
- Fork or deploy LRTDepositPool + LRTOracle + mock LST oracle.
- Deposit 100 ETH as user A; assert rsETHPrice = 1e18.
- Simulate reward accrual: send 10 ETH directly to LRTDepositPool (mimicking FeeReceiver).
- Deposit 10 ETH as attacker; record rsETH minted.
- Call updateRSETHPrice() as attacker.
- Assert newRsETHPrice < 1.1e18 (diluted from expected 1.1).
- Assert attacker rsETH value > 10 ETH (yield captured).
- Assert user A rsETH value < 110 ETH (yield stolen).
```

### Citations

**File:** contracts/LRTDepositPool.sol (L480-499)
```text
        ethLyingInDepositPool = address(this).balance;

        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;

        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L234-234)
```text
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
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
