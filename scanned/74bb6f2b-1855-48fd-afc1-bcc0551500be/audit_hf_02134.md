# [M] Lack of Slippage Control in _zapNativeToSecondaryWant()

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 11978
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
In the Dyson protocol, the MaximizerBalancer contract acts as the Maximizer strategy which keeps
harvesting the primary strategy, converts all the earned Want tokens into the secondaryWant tokens,
and stakes these secondaryWant tokens to the secondary vault to earn rewards. While reviewing the
logic to convert the Want tokens to the secondaryWant tokens, we notice there is no slippage control
for the token transformation.
To elaborate, we show below the code snippet of the MaximizerBalancer::_zapNativeToSecondaryWant() routine. After the earned Want tokens are withdrawn from the primary vault, they are converted to
the native tokens. Next, the _zapNativeToSecondaryWant() routine is used to zap the native tokens to
the secondaryWant tokens. At the beginning of the routine, half of the native tokens are converted to
the token0 of the secondaryWant. However, we notice the minimum output amount, i.e., amountOutMin,
is set to 0 (line 311), which means there is no slippage control in place for the swap. Similarly, there
is no slippage control either for the swap from the other half of the native tokens to the token1 of
the secondaryWant (line 316).
What is more, when the received token0/token1 are supplied to the secondaryRouter to add new
liquidity, the minimum amounts for token0/token1 are both set to 0 (lines 327 328), which means
there is no slippage control for the new liquidity adding.
function _zapNativeToSecondaryWant(uint256 nativeBalance) internal {
    require(IERC20Upgradeable(native).balanceOf(address(this)) >= nativeBalance, "zap: doesn't have enough native balance");
    uint256 nativeHalf = nativeBalance / 2;
    if (native != secondaryLpToken0) {
        IDystopiaRouter.Route[] memory routeArray = getRoute(
            routerUtils.getNativeToSecondaryLpToken0Route(),
            routerUtils.getIsStableNativeToSecondaryLpToken0()
        );
        IDystopiaRouter(routerUtils.secondaryRouter()).swapExactTokensForTokens(
            nativeHalf,
            0,
            routeArray,
            address(this),
            block.timestamp
        );
    }
    if (native != secondaryLpToken1) {
        IDystopiaRouter.Route[] memory routeArray = getRoute(
            routerUtils.getNativeToSecondaryLpToken1Route(),
            routerUtils.getIsStableNativeToSecondaryLpToken1()
        );
        IDystopiaRouter(routerUtils.secondaryRouter()).swapExactTokensForTokens(
            nativeHalf,
            0,
            routeArray,
            address(this),
            block.timestamp
        );
    }
    uint256 secondaryLpToken0Bal = IERC20Upgradeable(secondaryLpToken0).balanceOf(address(this));
    uint256 secondaryLpToken1Bal = IERC20Upgradeable(secondaryLpToken1).balanceOf(address(this));
    IDystopiaRouter(routerUtils.secondaryRouter()).addLiquidity(
        secondaryLpToken0,
        secondaryLpToken1,
        routerUtils.getIsStableSecondaryLp0LP1(),
        secondaryLpToken0Bal,
        secondaryLpToken1Bal,
        0,
        0,
        address(this),
        block.timestamp
    );
}
```
The lack of proper slippage control opens up the possibility for front-running and potentially
results in a smaller converted amount. Note that this is a common issue plaguing current AMM-
based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce
the market price, and a tailgating buy-back of the same amount plus the trade amount.
Such
sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the
trading user. As a mitigation, we may consider specifying the restriction on possible slippage caused
by the trade or referencing the TWAP or time-weighted average price of Dystopia. Nevertheless, we
need to acknowledge that this is largely inherent to current blockchain infrastructure and there is
still a need to continue the search efforts for an effective defense.
Note the same issue is also applicable to the MaximizerBalancer::_zapPrimaryWantToNative()/StrategyBalancerAC::swap()/addLiquidity() routines.
```

## Recommendation
Develop an effective mitigation to the above sandwich arbitrage to better protect the interests of users.
