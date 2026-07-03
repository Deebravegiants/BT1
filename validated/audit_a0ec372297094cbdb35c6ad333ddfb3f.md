Audit Report

## Title
Stale `rsETHPrice` Used in Deposit and Withdrawal Calculations Without Prior Update - (`contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

## Summary
`LRTOracle.rsETHPrice` is a stored state variable updated only when `updateRSETHPrice()` is explicitly called. Neither `depositETH()`/`depositAsset()` in `LRTDepositPool.sol` nor `initiateWithdrawal()`/`instantWithdrawal()` in `LRTWithdrawalManager.sol` call `updateRSETHPrice()` before using this value. When the stored price is stale and lower than the true current price (the normal condition as staking rewards accrue), depositors receive more rsETH than their deposit warrants, diluting accrued yield belonging to existing holders. A compounding factor is that `updateRSETHPrice()` itself reverts for non-managers when the price drift exceeds `pricePercentageLimit`, creating a forced window where the stale price is both exploitable and un-updatable by ordinary users.

## Finding Description
`LRTOracle.rsETHPrice` is declared as a plain `uint256` state variable at line 28 of `LRTOracle.sol`. It is only written inside `_updateRsETHPrice()`, which is invoked by the public `updateRSETHPrice()` or the manager-only `updateRSETHPriceAsManager()`.

**Deposit path:**
`depositETH()` / `depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()`:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
`lrtOracle.rsETHPrice()` is a plain getter for the stored variable. No call to `updateRSETHPrice()` precedes this.

**Withdrawal path:**
`initiateWithdrawal()` / `instantWithdrawal()` → `getExpectedAssetAmount()`:
```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
Again, the stored value is read directly without a prior update.

**`pricePercentageLimit` guard blocks non-manager updates:**
Inside `_updateRsETHPrice()`, if `newRsETHPrice > highestRsethPrice` and the increase exceeds `pricePercentageLimit`, the function reverts for any caller who is not a manager:
```solidity
if (isPriceIncreaseOffLimit) {
    if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
        revert PriceAboveDailyThreshold();
    }
}
```
This means that once rewards have accrued past the configured threshold, ordinary users cannot refresh the price, yet they can still deposit against the stale (lower) price.

**Why existing checks are insufficient:**
- The `minRSETHAmountExpected` slippage parameter in `depositETH`/`depositAsset` protects the depositor from receiving too little, not from receiving too much.
- The `_validatePrices` bounds check in `unlockQueue` applies only to the operator-called unlock path, not to user-initiated deposits or withdrawals.
- There is no on-chain staleness check or freshness timestamp on `rsETHPrice`.

## Impact Explanation
**Primary impact — Theft of unclaimed yield (High):**
As staking rewards accrue, the true rsETH price rises above the stored `rsETHPrice`. A depositor calling `depositETH` or `depositAsset` receives `(depositAmount × assetPrice) / staleLowerPrice` rsETH. Because the denominator is smaller than it should be, the depositor receives excess rsETH. When `updateRSETHPrice()` is subsequently called, the price adjusts upward, and the depositor's excess rsETH is now worth more. Redeeming it extracts yield that belonged to existing holders. This is a concrete, repeatable transfer of accrued yield from existing rsETH holders to the attacker, matching the "Theft of unclaimed yield" impact class.

**Secondary impact — Direct theft of funds (Critical, conditional):**
If `rsETHPrice` is stale-high (e.g., after a slashing event that has not yet been reflected), a withdrawer calling `initiateWithdrawal` or `instantWithdrawal` receives more underlying assets than their rsETH entitles them to. The downside-protection pause in `_updateRsETHPrice()` mitigates large decreases but does not cover decreases within the `pricePercentageLimit` band.

## Likelihood Explanation
The primary scenario (stale-low price on deposit) is continuous and requires no special conditions: staking rewards accrue at ~4% APY on LSTs, so the stored price drifts below the true price between every pair of `updateRSETHPrice()` calls. Any depositor can observe the on-chain `rsETHPrice` versus the computed current price (derivable from public `getTotalAssetDeposits` and `rsETH.totalSupply`) and time their deposit to capture the discrepancy. The `pricePercentageLimit` guard makes the window worse: once the drift exceeds the configured threshold, non-managers are blocked from refreshing the price, extending the exploitable window until a manager acts.

## Recommendation
Call `updateRSETHPrice()` atomically at the start of each price-sensitive entry point before any price-dependent computation:

```solidity
// In LRTDepositPool.depositETH() and depositAsset():
ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

// In LRTWithdrawalManager.initiateWithdrawal() and instantWithdrawal():
ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
```

If the `pricePercentageLimit` guard would revert for non-managers, the deposit/withdrawal should also revert (or the guard should be relaxed for atomic price-refresh-then-use patterns). Alternatively, expose a `currentRsETHPrice()` view that computes the live price without writing state, and use it in place of the stored variable.

## Proof of Concept
**Preconditions:** `pricePercentageLimit` is set to `1e16` (1%). Staking rewards have accrued since the last `updateRSETHPrice()` call. True rsETH price is `1.005e18`; stored `rsETHPrice` is `1.000e18` (0.5% drift, within the threshold so `updateRSETHPrice()` is still callable by anyone).

**Steps:**
1. Attacker observes on-chain: `rsETHPrice = 1.000e18`, computed true price ≈ `1.005e18`.
2. Attacker calls `depositETH{value: 1000 ether}(0, "")`.
3. `getRsETHAmountToMint(ETH_TOKEN, 1000e18)` computes: `(1000e18 × 1e18) / 1.000e18 = 1000e18` rsETH minted.
4. Correct amount at true price: `(1000e18 × 1e18) / 1.005e18 ≈ 995.02e18` rsETH.
5. Attacker receives `≈ 4.98e18` excess rsETH (≈ 0.5% of deposit).
6. Attacker (or anyone) calls `updateRSETHPrice()`. Price updates to `1.005e18`.
7. Attacker calls `initiateWithdrawal` and eventually `completeWithdrawal`, redeeming `1000e18` rsETH at `1.005e18` and receiving `≈ 1005 ETH` — extracting `≈ 5 ETH` of yield that belonged to existing holders.

**Foundry test plan:**
- Fork mainnet; deploy/configure contracts with a known `rsETHPrice`.
- Simulate reward accrual by directly increasing the EigenLayer strategy balance (or mock `getTotalAssetDeposits` return).
- Call `depositETH` without calling `updateRSETHPrice` first; assert minted rsETH > correct amount.
- Call `updateRSETHPrice`; assert attacker's rsETH redeems for more ETH than deposited.
- Fuzz over drift magnitude and deposit size to bound the extractable yield.