# [M] reclaimLiquidity

## Summary
Severity: Medium
Contest weight: 0.5927
Dataset id: 19650
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If `LP` wants to retrieve the `Liquidity` that has been lent out, it can set a `renewalCutoffTime` through `reclaimLiquidity()`. If the `borrower` does not voluntarily close, `liquidatePosition()` can be used to forcibly close the `position` after the loan expires.
```solidity
function liquidatePosition(
    DataStruct.ClosePositionParams calldata params,
    address borrower
) external override nonReentrant {
...
    if (
        !((closeCache.tokenFromPremium < liquidateCache.tokenFromOwed ||
            closeCache.tokenToPremium < liquidateCache.tokenToOwed) ||
            (lien.startTime < lps.getRenewalCutoffTime(lien.tokenId) &&
                lien.startTime + LOAN_TERM < block.timestamp))
    ) {
        revert Errors.LiquidationNotMet();
    }
```
To forcibly close the `position`, we still need to wait for the expiration `block.timestamp > lien.startTime + LOAN_TERM`.

But currently, `openPosition()` is not restricted by `renewalCutoffTime`, as long as there is `Liquidity`, we can open a position.

In this way, malicious borrowers can continuously occupy `Liquidity` by closing and reopening before expiration. For example:

  1. The borrower executes `open position`, LOAN_TERM = 7 days
  2. LP executes `reclaimLiquidity()` to retrieve `Liquidity`
  3. On the 6th day, borrower execute `closePosition()` -> `openPosition()`
  4. The new `lien.startTime = block.timestamp`
  5. LP needs to wait another `7 days`
  6. The borrower repeats the 3rd step, indefinitely postponing

The borrower may need to pay a certain `fee` when `openPosition()`. If the benefits can be expected, it is very cost-effective.

## Recommendation
It is recommended that when `openPosition()`, if the current time is less than `renewalCutoffTime + LOAN_TERM + 1 days`, do not allow new `positions` to be opened, giving `LP` a time window for retrieval.

Or set a new flag `TOKEN_CLOSE = true` to allow `lp` to specify that Liquidity will no longer be lent out.
```solidity
function openPosition(
    DataStruct.OpenPositionParams calldata params
) public override nonReentrant returns (uint96 lienId, uint256 collateralTo) {
...
    require(block.timestamp > (lps[params.tokenId].renewalCutoffTime + LOAN_TERM + 1 days),"LP Restrict Open ");
```
This is an interesting discovery. Our original thinking was after `reclaim`, LP can withdraw liquidity in one tx via multicall. But the problem here is that the already borrowed liquidity can be extended indefinitely. We should probably just restrict new positions to be opened if `reclaim` is called. And the suggested change is also valid. Thanks!
