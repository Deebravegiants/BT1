# [M] `PrePOMarket.setFinalLongPayout

## Summary
Severity: Medium
Contest weight: 0.4639
Dataset id: 17304
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract allows the market owner to set the final payout for long positions through the function setFinalLongPayout. The function does not contain a guard that prevents it from being called more than once after the market has been settled. Because the only check is that finalLongPayout must be greater than a constant MAX_PAYOUT, the owner can overwrite the previously recorded payout value after some users have already redeemed their tokens. When the payout is changed a second time, the accounting of the remaining collateral no longer matches the amount that must be paid out to the outstanding short (or long) tokens. As a result the market can become insolvent: users who try to redeem their remaining tokens receive less collateral than expected, or the transaction reverts because the contract does not hold enough funds. The vulnerability is triggered when the owner calls setFinalLongPayout, users redeem a portion of their tokens, and then the owner calls setFinalLongPayout again with a different value that reduces the remaining pool of collateral. Any token holder – long or short – is affected because the protocol’s guarantee that the total collateral equals the sum of payouts is broken. The issue was discovered during a manual audit that simulated a scenario with a single user (Bob) who first redeemed long tokens at a payout of 60 % of the collateral, leaving 40 % in the contract, and then the owner reduced the finalLongPayout to 40 %, causing the short token redemption to request 60 % of collateral while only 40 % remained. The problem is subtle because the function is owner‑only and appears to be a one‑time finalisation step, so developers may assume it cannot be abused. To remediate, the contract should enforce a one‑time finalisation rule, for example by checking that finalLongPayout is still set to a sentinel value (e.g., MAX_PAYOUT) before allowing an update, or by introducing a boolean flag that is set after the first successful call and prevents any further modifications. This ensures that once the market is settled, the payout values cannot be altered, preserving the invariant that total collateral equals the sum of long and short payouts and preventing users from receiving less than the promised amount or seeing funds disappear.

## Proof of Concept
If `finalLongPayout` is less than `MAX_PAYOUT`, it means the market is ended and `longToken Price = finalLongPayout, shortToken Price = MAX_PAYOUT - finalLongPayout`.

So when users redeem their long/short tokens, the total amount of collateral tokens will be the same as the amount that users transferred during `mint()`.

Btw in `setFinalLongPayout()`, there is no validation that this function can’t be called twice and the below scenario would be possible.

1. Let’s assume there is one user `Bob` in the market for simplicity.
2. `Bob` transferred 100 amounts of `collateral` and got 100 long/short tokens. The market has 100 `collateral`.
3. The market admin set `finalLongPayout = 60 * 1e16` and `Bob` redeemed 100 `longToken` and received 60 `collateral`. The market has 40 `collateral` now.
4. After that, the admin realized `finalLongPayout` is too high and changed `finalLongPayout = 40 * 1e16` again.
5. `Bob` tries to redeem 100 `shortToken` and receive 60 `collateral` but the market can’t offer as it has 40 `collateral` only.

When there are several users in the market, some users can’t redeem their long/short tokens as the market doesn’t have enough `collaterals`.

## Recommendation
We should modify `setFinalLongPayout()` like below so it can’t be finalized twice.
    
```solidity
function setFinalLongPayout(uint256 _finalLongPayout) external override onlyOwner { 
  require(finalLongPayout > MAX_PAYOUT, "Finalized already"); //++++++++++++++++++++++++

  require(_finalLongPayout >= floorLongPayout, "Payout cannot be below floor");
  require(_finalLongPayout <= ceilingLongPayout, "Payout cannot exceed ceiling");
  finalLongPayout = _finalLongPayout;
  emit FinalLongPayoutSet(_finalLongPayout);
}
```
