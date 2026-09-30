# [H] Bonder can bypass the 1% of capital pool unbonding limit

## Summary
Severity: High
Contest weight: 0.5858
Dataset id: 22756
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Bypass of unbonding amount limit can cause liquidity issues and big losses to other contributers. When unbonding there is a check that the amount to unbond does not exceed 1% de/blob/main/FairsideContractsV2/contracts/token/FSD.sol#L334
```solidity
function unbond(uint256 capitalDesired, uint256 tokenMaximum) external {
    uint256 curveCapital = getReserveBalance();
    uint256 tribute = capitalDesired.mul(tributeFee);
    uint256 reserveWithdrawn = capitalDesired - tribute;
    if (staker.amountUnbonded + reserveWithdrawn > getCapitalPool().mul(0.01 ether)) {
        revert FSD_ExceedsOnePercentOfCapitalPool();
    }
}
```
This can be easily bypassed by splitting the unbonding operation to multiple accounts. The user will send their FSD to multiple user owned accounts and call unbond from each one - not exceeding the 1% limit per user. Users will be able to unbond large amount of funds. This will create a liquidity pinch. Users that will see the large unbond (possibly in mempool) will see it profitable for them to unbond before (losses of 3.5% fee will be less then the loss of a big unbond).

## Recommendation
Either limit the 1% to be per day globally (not per user) - giving enough time to react. Or add the same limitation to _beforeTokenTransfer hook (not allow sending more then 1% of capital pool per day).
