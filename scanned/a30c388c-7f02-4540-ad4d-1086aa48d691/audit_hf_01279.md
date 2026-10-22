# [M] The slippage protection in the MicroManager does not account for the harvested rewards

## Summary
Severity: Medium
Contest weight: 0.4333
Dataset id: 6032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The boringVault allows strategies to execute trades to manage the portfolio. To prevent strategies from draining the BoringVault, the MicroManager includes a slippage check to ensure that the value withdrawn is not smaller than the value deposited.  
```solidity
ERC20 tokenOut = path[path.length - 1];
uint256 tokenOutBalanceDelta = tokenOut.balanceOf(boringVault);
// Make the manage call.
manager.manageVaultWithMerkleVerification(manageProofs, decodersAndSanitizers, targets, targetData, values);
tokenOutBalanceDelta = tokenOut.balanceOf(boringVault) - tokenOutBalanceDelta;
uint256 tokenOutQuotedInTokenIn = priceRouter.getValue(tokenOut, tokenOutBalanceDelta, path[0]);
if (tokenOutQuotedInTokenIn < amountIn.mulDivDown(1e4 - allowedSlippage, 1e4)) {
    revert DexSwapperUManager__Slippage();
}
```
Since the slippage protection only considers the value of tokens withdrawn and the tokens increased within the swaps, exploiters can steal the harvested rewards.  
Let's assume the boringVault holds a large position in Pendle Finance's YT Token and is nearing the settlement time. The exploiter can execute the following steps:  
1. Initiate a trade that simply transfers tokens to the exploiter's wallet.  
2. Claim rewards for the boringVault. Similar to most claimRewards functions, Pendle Finance allows anyone to claim interests for other users through redeemDueInterestAndRewards.  
3. As the tokens are increased, the slippage protection is bypassed.

## Recommendation
Consider sanitizing the entire swap path of a trade to prevent the initiator from gaining control of the flow.
