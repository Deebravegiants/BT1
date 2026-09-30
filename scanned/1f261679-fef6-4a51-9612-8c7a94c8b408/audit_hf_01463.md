# [H] Ineffective deadline check

## Summary
Severity: High
Contest weight: 0.3206
Dataset id: 7622
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deadline parameter in swapExactTokensForETHSupportingFeeOnTransferTokens() and
addLiquidityETH() which are called in swapTokensForEth() and addLiquidity() is hard coded to
block.timestamp.
Example in addLiquidity():
function addLiquidity(uint256 tokenAmount, uint256 ethAmount) private {
tokenAmount, 0, 0, owner(), block.timestamp); ///@audit here is the
problem
The addLiquidityETH() in UniswapV2Router02 contract:
function addLiquidityETH(
uint amountTokenDesired,
uint amountTokenMin,
uint amountETHMin,
uint deadline
) external virtual override payable ensure(deadline) returns (uint
amountToken, uint amountETH, uint liquidity)
The deadline parameter enforces a time limit by which the transaction must be executed otherwise it will
revert.
Lets take a look at a modifier which is present in the functions you are calling in UniswapV2Router02
contract:
modifier ensure(uint deadline) {
require(deadline >= block.timestamp, 'UniswapV2Router: EXPIRED');
Now when the deadline is hardcoded as block.timestamp, the transaction will not revert because the
require statement will always be fulfilled by block.timestamp == block.timestamp.
If a user chose a transaction fee that is too low for miners to be interested in including the transaction in a
block, the transaction stays pending in the mempool for extended periods, which could be hours, days,
weeks, or even longer.
This could lead to users getting a worse price, because a validator can just hold onto the transaction.

## Recommendation
Protocols should let users who interact with AMMs set expiration deadlines. Without this, there's a risk of a
serious loss of funds for anyone starting a swap, especially if there's no slippage parameter.
Use a user supplied deadline instead of block.timestamp.
