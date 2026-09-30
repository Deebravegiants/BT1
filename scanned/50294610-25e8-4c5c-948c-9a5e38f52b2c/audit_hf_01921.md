# [H] Deadline check is not effective

## Summary
Severity: High
Contest weight: 0.7817
Dataset id: 10540
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deadline parameter in swapExactTokensForETHSupportingFeeOnTransferTokens() and
addLiquidityETH() which are called in swapTokensForEth() and openTrade() is hardcoded to
block.timestamp.
Example in openTrade():
```solidity
function openTrade() external payable onlyOwner {
    0, //uint amountTokenMin,
    0, //uint amountETHMin,
    owner(),
    block.timestamp
}
```
The addLiquidityETH() in UniswapV2Router02 contract:
```solidity
function addLiquidityETH(
    uint amountTokenDesired,
    uint amountTokenMin,
    uint amountETHMin,
    uint deadline
) external virtual override payable ensure(deadline) returns (uint amountToken, uint amountETH, uint liquidity)
```
The deadline parameter enforces a time limit by which the transaction must be executed otherwise it will
revert.
Let's take a look at a modifier that is present in the functions you are calling in UniswapV2Router02
contract:
```solidity
modifier ensure(uint deadline) {
    require(deadline >= block.timestamp, 'UniswapV2Router: EXPIRED');
}
```
Now when the deadline is hardcoded as block.timestamp, the transaction will not revert because the
require statement will always be fulfilled by block.timestamp == block.timestamp.
If a user chooses a transaction fee that is too low for miners to be interested in including the transaction in a
block, the transaction stays pending in the mempool for extended periods, which could be hours, days,
weeks, or even longer.
This could lead to users getting a worse price because a validator can just hold onto the transaction.
Recommendations
Protocols should let users who interact with AMMs set expiration deadlines. Without this, there's a risk of a
serious loss of funds for anyone starting a swap, especially if there's no slippage parameter.
Use a user-supplied deadline instead of block.timestamp.

## Recommendation
Protocols should let users who interact with AMMs set expiration deadlines. Without this, there's a risk of a
serious loss of funds for anyone starting a swap, especially if there's no slippage parameter.
Use a user-supplied deadline instead of block.timestamp.
