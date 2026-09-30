# [M] Withdrawals will revert when a pool contains

## Summary
Severity: Medium
Contest weight: 0.4011
Dataset id: 22926
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdrawals will revert when a pool contains a velodrome NFT staked in a killed gauge. The withdrawal flow for staked velodrome/slipstrem NFT positions is arranged by VelodromeCLAssetGuard::withdrawProcessing(). Among others, there are 3 key operations arranged: 1. Withdraw the NFT from the gauge 2. Decrease the liquidity 3. Re-deposit the NFT in the gauge The deposit is performed if any liquidity is left in the NFT position via a call to the CLGauge:deposit() function in the corresponding gauge, but this call fails if the gauge has been killed:

```solidity
function deposit(uint256 tokenId) external override nonReentrant {
    require(nft.ownerOf(tokenId) == msg.sender, "NA");
    ...
}
```

It will be impossible to withdraw funds because the PoolLogic::_withdrawTo() function will revert when trying to re-deposit the NFT in the killed gauge. This can

## Recommendation
In VelodromeCLAssetGuard::_addDecreaseLiquidityTransactions() don't add the transaction to re-deposit the NFT if the gauge is killed.
