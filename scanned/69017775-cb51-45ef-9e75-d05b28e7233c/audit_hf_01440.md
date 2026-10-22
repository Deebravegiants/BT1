# [H] Lost rewards due to updating shares in _sellShares() before calculating rewards

## Summary
Severity: High
Contest weight: 0.5403
Dataset id: 7458
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SpaceShare contract implements MasterChef style rewards by using a rewards accumulator. However, in _sellShares(), the user shares balance (and the total supply) are updated before calculating the user rewards from the previous period, leading to the user losing these rewards. See the poc here for confirmation.

## Recommendation
Update the rewards before changing the user shares and total supply.
```solidity
function _sellShares(uint256 spaceId, uint256 shares, uint256 minOutAmount)
internal returns (uint256 outAmount) {
    ...
    _updateSharesReward(spaceId, holderFee, trader); //@audit place here the rewards update and remove below
    uint256 totalSupply;
    unchecked {
        sharesBalance[spaceId][trader] -= shares;
        totalSupply = supply - shares;
    }
    sharesSupply[spaceId] = totalSupply;
    ...
}
```
