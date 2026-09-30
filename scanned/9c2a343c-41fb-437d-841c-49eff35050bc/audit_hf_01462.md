# [H] Lack of slippage control can lead to sandwich attacks

## Summary
Severity: High
Contest weight: 0.2150
Dataset id: 7621
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The amountOutMin parameter in swapExactTokensForETHSupportingFeeOnTransferTokens is
hard coded to 0 in swapTokensForEth():
function swapTokensForEth(uint256 tokenAmount) private lockTheSwap {
path[1] = uniswapV2Router.WETH();
uniswapV2Router.swapExactTokensForETHSupportingFeeOnTransferTokens(
tokenAmount,
0,
path,
block.timestamp
This basically allows for 100% slippage as the call agrees to receive 0 amount of ETH for the swap. This can
be done through a sandwich attack. The same applies to the addLiquidity function:
function addLiquidity(uint256 tokenAmount, uint256 ethAmount) private {
tokenAmount, 0, 0, owner(), block.timestamp);
This is a very easy target for MEV and bots to do a flash loan sandwich attack and can be done on every call
if the trade transaction goes through a public mempool.

## Recommendation
The best solution to this problem is to add an input parameter instead of hardcoding 0. The amountOutMin
can be calculated off-chain and agreed upon by the user and can be passed to the call. This will protect the
calls from sandwich attacks.
