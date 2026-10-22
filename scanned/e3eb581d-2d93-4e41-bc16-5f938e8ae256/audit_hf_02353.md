# [M] Extra Funds Return in swapV2ExactIn()/swapV3MultiHopExactIn()

## Summary
Severity: Medium
Contest weight: 0.4607
Dataset id: 12762
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function swapV2ExactIn(
    address tokenIn,
    address tokenOut,
    uint256 amountIn,
    uint256 amountOutMin,
    address poolAddress
) payable public nonReentrant whenNotPaused returns (uint amountOut){
    require(poolAddress != address(0), "SwapX: invalid pool address");
    require(amountIn > 0, "SwapX: amout in is zero");
    uint256 fee = takeFee(tokenIn, amountIn);
    amountIn = amountIn - fee;
    bool nativeOut = false;
    if (tokenOut == address(0))
        nativeOut = true;
    if (tokenIn == address(0)) {
        require(msg.value >= amountIn + fee, "SwapX: amount in and value mismatch");
        tokenIn = WETH;
        pay(tokenIn, address(this), poolAddress, amountIn);
    } else
        pay(tokenIn, msg.sender, poolAddress, amountIn);
    uint balanceBefore = nativeOut ? IERC20Upgradeable(WETH).balanceOf(address(this)) : IERC20Upgradeable(tokenOut).balanceOf(msg.sender);
    IUniswapV2Pair pair = IUniswapV2Pair(poolAddress);
    address token0 = pair.token0();
    uint amountInput;
    uint amountOutput;
    { // scope to avoid stack too deep errors
        (uint reserve0, uint reserve1,) = pair.getReserves();
        (uint reserveInput, uint reserveOutput) = tokenIn == token0 ? (reserve0, reserve1) : (reserve1, reserve0);
        amountInput = IERC20Upgradeable(tokenIn).balanceOf(address(pair)).sub(reserveInput);
        amountOutput = UniswapV2Library.getAmountOut(amountInput, reserveInput, reserveOutput);
        (uint amount0Out, uint amount1Out) = tokenIn == token0 ? (uint(0), amountOutput) : (amountOutput, uint(0));
        address to = nativeOut ? address(this) : msg.sender;
        pair.swap(amount0Out, amount1Out, to, new bytes(0));
    }
    if (nativeOut) {
        amountOut = IERC20Upgradeable(WETH).balanceOf(address(this)).sub(balanceBefore);
        IWETH(WETH).withdraw(amountOut);
        (bool success, ) = address(msg.sender).call{value: amountOut}("");
        require(success, "SwapX: send ETH out error");
    } else {
        amountOut = IERC20Upgradeable(tokenOut).balanceOf(msg.sender).sub(balanceBefore);
        require(
            amountOut >= amountOutMin,
            "SwapX: insufficient output amount"
        );
    }
}
```
To facilitate the token swaps, the SwapX protocol supports a set of well-defined interfaces that allow the user to specify the exact input amount or expected output amount. While examining two specific functions, e.g., swapV2ExactIn() and swapV3MultiHopExactIn(), we notice the possibility of receiving extra native coins from the trading user and these extra coins can be better returned back to the user. To elaborate, we show below the swapV2ExactIn() routine implementation. This routine allows the user to directly swap native coins in ETH to another token. And it comes to our attention that current implementation only validates the input amount is sufficient (line 174), but does not return the extra funds back.

## Recommendation
Return any extra fund, if any, back to the trading user. Note both swapV2ExactIn() and swapV3MultiHopExactIn() routines share this issue.
