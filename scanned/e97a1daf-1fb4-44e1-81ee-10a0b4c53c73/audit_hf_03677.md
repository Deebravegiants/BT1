# [M] Depositing GNS might revert before reaching

## Summary
Severity: Medium
Contest weight: 0.4132
Dataset id: 19770
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deposit function is checking the balance after deposit to verify that it does not exceeds the maximum threshold maxGNSDeposit set into the contract. However, the check does not take the fees into account. Therefore, the function might revert in maximum threshold
The deposit function is checking the future balance of GNS against the maximum threshold set into the contract. This is done in the function below:
```solidity
function deposit(uint256 assets, address receiver) public virtual override returns (uint256) {
    require(totalAssets() + assets <= maxGNSDeposited(), "GNS deposits more than max"); <==========================
    compound();
    assets = sendDepositFees(assets);
    uint256 shares = super.deposit(assets, receiver);
    stakeGNS();
    return shares;
}
```
amount of GNS deposited should be totalAssets() + assets - fees instead of totalAssets() + assets.
that this is properly handled in the mint function though because the check is done once every amounts have been taking into account (deposit, fees and rewards).
deposit might revert while it should not.

## Recommendation
Replicate what is done in mint, i.e., make the check after all amounts are taken into account in the balance.
