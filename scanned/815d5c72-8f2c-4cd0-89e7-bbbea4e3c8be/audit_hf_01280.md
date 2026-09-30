# [M] Malicious strategies can bypass slippage protection to drain the BoringVault with Reentrancy attacks

## Summary
Severity: Medium
Contest weight: 0.4259
Dataset id: 6033
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
However, due to the lack of re-entrancy protection, the exploiter can interact with protocol within the swap execution and change the token balance, the slippage protection may be off.  
A malicious payload could exploit the following scenario:  
1. Execute a malicious swap that transfers all tokens to the attacker's wallet.  
2. Deposit tokens into the boringVault and receive vault shares.  
3. As the balance of the boringVault increases, the slippage protection is bypassed.  
4. Withdraw the vault shares and obtain the profit.

## Recommendation
Add a protocol-wise reentrancy protection to prevent this attack.
