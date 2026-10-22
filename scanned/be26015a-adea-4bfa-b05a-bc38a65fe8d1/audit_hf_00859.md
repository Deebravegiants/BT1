# [M] Withdrawing all lv before expiry

## Summary
Severity: Medium
Contest weight: 0.6012
Dataset id: 2597
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
VaultLib:redeemEarly() redeems users' liquidity vault positions, lv for Ra, before expiry.
After expiry, it is not possible to deposit into the vault or redeem early.
Whenever all users redeem early, when it gets to the expiry date, VaultLib::_liquidatedLp() is called to remove the lp position from the AMM into Ra and Ct (redeem from the PSM into more Ra and Pa) and split among all lv holders.
However, as the total supply of lv is 0 due to users having redeemed all their positions via VaultLib::redeemEarly(), when it gets to VaultPoolLib::reserve(), it reverts due to a division by 0 error, never allowing the Vault::_liquidatedLp() call to go through.
As the Ds has expired, it is also not possible to deposit into it to increase the lv supply, so all funds are forever stuck.
In MathHelper:134, the ratePerLv reverts due to division by 0. It should calculate the rate after the return guard that checks if the totalLvIssued==0.

Internal pre-conditions
1. All users must redeem early.

External pre-conditions
None.

Attack Path
1. All users redeem early via Vault::redeemEarlyLv().
2. The Ds expires and there is no lv tokens, making all funds stuck.
All funds are stuck.

## Proof of Concept
The MathHelper separates liquidity by calculating first the ratePerLv, which will trigger a division by 0 revert.
```solidity
function separateLiquidity(uint256 totalAmount, uint256 totalLvIssued, uint256 totalLvWithdrawn)
    external
    pure
    returns (uint256 attributedWithdrawal, uint256 attributedAmm, uint256 ratePerLv)
{
    // with 1e18 precision
    ratePerLv = ((totalAmount * 1e18) / totalLvIssued);
    // attribute all to AMM if no lv issued or withdrawn
    if (totalLvIssued == 0 || totalLvWithdrawn == 0) {
        return (0, totalAmount, ratePerLv);
    }
    ...
}
```

## Recommendation
The MathHelper should place the return guard first:
```solidity
function separateLiquidity(uint256 totalAmount, uint256 totalLvIssued, uint256 totalLvWithdrawn)
    external
    pure
    returns (uint256 attributedWithdrawal, uint256 attributedAmm, uint256 ratePerLv)
{
    // attribute all to AMM if no lv issued or withdrawn
    if (totalLvIssued == 0 || totalLvWithdrawn == 0) {
        return (0, totalAmount, 0);
    }
    ...
    // with 1e18 precision
    ratePerLv = ((totalAmount * 1e18) / totalLvIssued);
}
```
