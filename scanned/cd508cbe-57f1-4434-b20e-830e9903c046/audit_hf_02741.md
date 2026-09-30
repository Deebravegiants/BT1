# [H] Wrong Amount in sponsorSeries

## Summary
Severity: High
Contest weight: 0.5598
Dataset id: 15008
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Situation:
In function sponsorSeries(), a different amount is used with safeTransferFrom() than with safeApprove(), if the number of decimals of the stake token != 18.
Normally, safeTransferFrom() and safeApprove() should be the same amount.
```solidity
function sponsorSeries(address adapter, uint48 maturity) external returns (address zero, address claim) {
    ...
    // Transfer stakeSize from sponsor into this contract
    uint256 stakeDecimals = ERC20(stake).decimals();
    ERC20(stake).safeTransferFrom(msg.sender, address(this), _convertToBase(stakeSize, stakeDecimals)); // amount 1
    // Approve divider to withdraw stake assets
    ERC20(stake).safeApprove(address(divider), stakeSize); // amount 2
}
```

## Recommendation
Spearbit recommends double checking which of these two amounts is the right amount and update the code. We also recommend considering adding unit tests with Stake tokens with less than 18 decimals.
