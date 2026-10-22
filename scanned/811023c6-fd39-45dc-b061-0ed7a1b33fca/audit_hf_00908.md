# [H] vePeg#deposit_for fails to increment perpetualLockAmount leading to incorrect supply values

## Summary
Severity: High
Contest weight: 0.5716
Dataset id: 2712
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[vePeg.sol#L757-L764](https://github.com/hyperstable/contracts/blob/4f650122d3927fd45015c40ad58172508b148876/src/governance/vePeg.sol#L757-L764)

```solidity
function deposit_for(uint256 _tokenId, uint256 _value) external nonreentrant {
    LockedBalance memory _locked = locked[_tokenId];

    require(_value > 0); // dev: need non-zero value
    require(_locked.amount > 0, "No existing lock found");
    require(_locked.end > block.timestamp, "Cannot add to expired lock. Withdraw");
    _deposit_for(_tokenId, _value, 0, _locked, DepositType.DEPOSIT_FOR_TYPE);
}
```

perpetualLockAmount is used to track the total supply of points across all tokens that have been locked perpetually and is essential for properly tracking the total supply. Above we see that the amount of tokens locked increases but perpetualLockAmount is not correctly incremented with the amount being added. This leads to an inaccurate total supply and over allocation of tokens.

## Recommendation
perpetualLockAmount should be incremented by _value.
