# [M] Incorrect principle tracking due to fee inclusion

## Summary
Severity: Medium
Contest weight: 0.4000
Dataset id: 14796
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the deposit function, the principle state variable is incorrectly updated by adding the full deposit amount, including fees that are not actually staked:

```solidity
function deposit(uint256 amount) external whenNotPaused returns (uint256 mintedAmount) {
    // Calculate fees
    (mintedAmount, stakingFee) = _calculateMintAmountAndFees(amount);
    // Incorrect: Updates principle with full amount including fees
    principle += amount; // @audit - includes stakingFee and bridgingFee
    // Transfer and mint logic...
    IERC20(underlyingToken).safeTransfer(protocolVault, stakingFee);
    bool success = _bridge(mintedAmount + bridgingFee);
```

The principle should only track the actual staked amount (mintedAmount) rather than the total deposit amount which includes: Staking fee (stakingFee), Bridging fee (bridgingFee), Actually staked amount (mintedAmount).

## Recommendation
Update the principle to only include the actual staked amount.
