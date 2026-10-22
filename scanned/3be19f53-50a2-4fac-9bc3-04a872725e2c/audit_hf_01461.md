# [C] Wrong router is hardcoded and _transfer will be bricked

## Summary
Severity: Critical
Contest weight: 0.1092
Dataset id: 7620
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The IUniswapV2Router02 interface is implemented and two of it's functions are called during a transfer -
swapExactTokensForETHSupportingFeeOnTransferTokens and addLiquidityETH. The problem
IUniswapV2Router02 _uniswapV2Router =
IUniswapV2Router02(0xfCD3842f85ed87ba2889b4D35893403796e67FF1); //@audit -
is problematic because the addLiquidityETH of LeetSwapRouter is different from UniswapV2Router:
function addLiquidityETH(
uint256 amountTokenDesired,
uint256 amountTokenMin,
uint256 amountCANTOMin,
uint256 deadline
external
payable
ensure(deadline)
returns (
uint256 amountToken,
uint256 amountCANTO,
uint256 liquidity
bool isStable = stablePairs[pair];
(amountToken, amountCANTO) = _addLiquidity(
token,
isStable,
amountTokenDesired,
msg.value,
amountTokenMin,
amountCANTOMin
_safeTransferFrom(token, msg.sender, pair, amountToken);
wcanto.deposit{value: amountCANTO}();
assert(wcanto.transfer(pair, amountCANTO));
liquidity = ILeetSwapV2Pair(pair).mint(to);
// refund dust eth, if any
if (msg.value > amountCANTO) {
_safeTransferETH(msg.sender, msg.value - amountCANTO);
(bool success, ) = to.call{value: value}(new bytes(0));
if (!success) revert CantoTransferFailed();
As you can see from the code snippet above the function works with wrapped Canto while the wrapped
ETH is expected for the UniswapV2Router. This will lead to bricking the transfer function unless wCanto is
provided every it is called.

## Recommendation
There are 2 possible solutions here:
). Use the actual UniswapV2Router.
*. Use the LeetSwapRouter interface but refactoring of the code will be required.
