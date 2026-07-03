Audit Report

## Title
`updateRSETHPrice()` Permanently Blocked When Fee Exceeds `maxFeeMintAmountPerDay`, Freezing Protocol Fee Yield and Staling rsETH Price — (File: contracts/LRTOracle.sol)

## Summary

`_updateRsETHPrice()` calls `_checkAndUpdateDailyFeeMintLimit` before writing `rsETHPrice`, so a revert from `DailyFeeMintLimitExceeded` leaves the stored price stale. Because `maxFeeMintAmountPerDay` defaults to `0` and the stale price causes an ever-growing fee gap on each subsequent call, the block is self-reinforcing: protocol fee yield is permanently frozen and the rsETH exchange rate becomes stale until a manager raises the limit.

## Finding Description

`maxFeeMintAmountPerDay` is a storage variable that initialises to `0`:

```solidity
// contracts/LRTOracle.sol line 35
uint256 public maxFeeMintAmountPerDay;
```

With the default value of `0`, the check at lines 205–206 reverts for any non-zero fee amount, because `0 + feeAmount > 0` is always true:

```solidity
// contracts/LRTOracle.sol lines 205-206
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(...);
}
```

The revert occurs at line 303, before `rsETHPrice = newRsETHPrice` at line 313, so the price is never written:

```solidity
// contracts/LRTOracle.sol lines 303, 313
_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);  // reverts here
...
rsETHPrice = newRsETHPrice;  // never reached
```

On every subsequent call, `previousTVL` is computed from the stale (lower) `rsETHPrice`:

```solidity
// contracts/LRTOracle.sol lines 234, 245-246
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
...
uint256 rewardAmount = totalETHInProtocol - previousTVL;
protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
```

Because `rsETHPrice` is stale, `rewardAmount` grows with each missed update, producing an even larger fee that again exceeds the limit. The daily period reset (`currentPeriodMintedFeeAmount = 0`) does not help because the per-call fee amount itself exceeds `maxFeeMintAmountPerDay`. The block is self-reinforcing and persists indefinitely without manager intervention.

The downside-protection circuit-breaker at lines 269–281 is also unreachable because the function always reverts before that logic executes.

## Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Protocol fee tokens that should be minted to the treasury are never created for as long as the block persists. The longer the block persists, the larger the deferred fee grows, making recovery harder. Additionally, `rsETHPrice` remains stale, causing `LRTWithdrawalManager` to compute withdrawal amounts using an outdated (lower) exchange rate, and the auto-pause circuit-breaker is inoperative. This matches the allowed impact: *Medium. Permanent freezing of unclaimed yield.*

## Likelihood Explanation

**Medium.** No attacker action is required. The condition is triggered by normal protocol operation:

1. `maxFeeMintAmountPerDay` defaults to `0` — if the manager never calls `setMaxFeeMintAmountPerDay`, any non-zero fee immediately causes a revert.
2. Even if set to a reasonable value at launch, significant TVL growth or an extended pause (e.g., network congestion, deliberate pause) causes the accumulated reward to spike above the cap on the next call.
3. Once triggered, the block is self-reinforcing without further action from anyone.
4. The only remediation is a manager transaction to raise `maxFeeMintAmountPerDay`.

## Recommendation

Replace the hard revert in `_checkAndUpdateDailyFeeMintLimit` with a cap-and-carry or skip approach so that `_updateRsETHPrice` always completes and `rsETHPrice` is always written. For example, mint only up to the remaining daily allowance and defer the rest, or skip fee minting for the period without reverting:

```solidity
uint256 remaining = maxFeeMintAmountPerDay - currentPeriodMintedFeeAmount;
uint256 mintableNow = feeAmount > remaining ? remaining : feeAmount;
currentPeriodMintedFeeAmount += mintableNow;
return mintableNow; // caller mints only this amount
```

This ensures `rsETHPrice` is always updated, the circuit-breaker always has the opportunity to fire, and fee yield is never permanently frozen.

## Proof of Concept

1. Deploy with `maxFeeMintAmountPerDay = 0` (default — manager never calls `setMaxFeeMintAmountPerDay`).
2. Staking rewards accrue; `totalETHInProtocol` grows above `rsethSupply * rsETHPrice`.
3. Anyone calls `updateRSETHPrice()` (public, no privilege required).
4. `protocolFeeInETH > 0` → `rsethAmountToMintAsProtocolFee > 0`.
5. `_checkAndUpdateDailyFeeMintLimit` reverts: `0 + feeAmount > 0`.
6. `rsETHPrice` is not updated; fee is not minted.
7. Wait 24 h (daily period resets, `currentPeriodMintedFeeAmount = 0`). Call again.
8. `previousTVL` is computed from the still-stale `rsETHPrice`; `rewardAmount` is now larger (48 h of rewards); fee exceeds limit again → revert.
9. The block persists indefinitely. Treasury receives no fee yield. Withdrawals use the stale lower price. The auto-pause circuit-breaker never fires.

Foundry test sketch:
```solidity
function test_feeMintBlockSelfReinforcing() public {
    // maxFeeMintAmountPerDay is 0 by default
    // simulate reward accrual by increasing mock oracle price
    mockOracle.setPrice(asset, initialPrice * 101 / 100);
    vm.expectRevert(LRTOracle.DailyFeeMintLimitExceeded.selector);
    lrtOracle.updateRSETHPrice();
    // price unchanged
    assertEq(lrtOracle.rsETHPrice(), initialRsETHPrice);
    // advance 24h, try again — fee is now larger, still reverts
    vm.warp(block.timestamp + 1 days);
    vm.expectRevert(LRTOracle.DailyFeeMintLimitExceeded.selector);
    lrtOracle.updateRSETHPrice();
}
```