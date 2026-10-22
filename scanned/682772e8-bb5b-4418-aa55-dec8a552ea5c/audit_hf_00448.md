# [M] WasabiRouter::swapVaultToToken

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 1872
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
WasabiRouter::swapVaultToToken - Function can be DoSed
```
swapVaultToToken performs:
1. Withdraws from a vault in the name of the sender.
2. Either: 2.1 Unwraps the withdrawn WETH from the vault and sends it to msg.sender 2.2 Performs a swap between the withdrawn asset and another token. 2.3 Simply transfers the withdrawn asset to msg.sender.
3. Before finishing the tx it checks:
```solidity
// SwapRouter should transfer tokenOut directly to user (and fee receiver)
if (_tokenOut == address(0)) {
    if (address(this).balance != 0) revert InvalidETHReceived();
} else if (IERC20(_tokenOut).balanceOf(address(this)) != 0) {
    revert InvalidTokensReceived();
}
```
If either of these is true the tx will revert. These checks can very easily be abused and will almost completely brick the function.
```solidity
if (address(this).balance != 0)
```
The contract has a receive that can only be called from weth and the swapRouter, but the contract can be forcefully sent native tokens using selfdestruct.
```solidity
else if (IERC20(_tokenOut).balanceOf(address(this)) != 0)
```
Anyone can just transfer 1 wei _tokenOut to the contract.
The only way to currently ”fix” this, is by calling swapTokenToVault (swapVaultToVault might also work), since at the end any tokens either native or ERC20 are refunded back to msg.sender.
```solidity
// If full amount of tokenIn was not used, return it to the user
if (isETHSwap) {
    uint256 amountRemaining = address(this).balance;
    if (amountRemaining != 0) {
        payable(msg.sender).sendValue(amountRemaining);
    }
} else {
    uint256 amountRemaining = IERC20(_tokenIn).balanceOf(address(this));
    if (amountRemaining != 0) {
        IERC20(_tokenIn).safeTransfer(msg.sender, amountRemaining);
    }
}
```
This will ”fix” swapVaultToToken, but the function can be attacked immediately after.
Breaking of core functionality, DoS of the function which can easily be repeated

## Recommendation
The easiest solution would be to just remove the two checks, but if you want to keep them you cannot revert, as it open up this attack vector.
