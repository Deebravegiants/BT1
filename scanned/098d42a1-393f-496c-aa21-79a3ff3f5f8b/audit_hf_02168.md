# [M] Potential Sandwich/MEV Attack For zapOutToPair()

## Summary
Severity: Medium
Contest weight: 0.4592
Dataset id: 12096
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the FireBirdZap contract, we notice the zapOutToPair() function is used to exchange the LP Token to two different kinds of tokens in the pair on behalf of msg.sender. The pair is specified by the first input argument _from of the zapOutToPair() function.  
We notice the zapOutToPair() transaction is routed to FireBirdRouter or UniswapV2Router. We will take FireBirdRouter as our example. The FireBirdRouter::removeLiquidity() is called in line 114 to exchange LP Token to two different kinds of tokens in the pair. We observe the fifth input argument amountAMin and the sixth input argument amountBMin of the FireBirdRouter::removeLiquidity() function are both 1, which means this transaction does not specify any restriction on possible slippage and is therefore vulnerable to possible front-running attacks.  
```solidity
// _from: must be a pair lp
function zapOutToPair(address _from, uint amount) public nonReentrant returns (uint256 amountA, uint256 amountB) {
    IERC20(_from).safeTransferFrom(msg.sender, address(this), amount);
    _approveTokenIfNeeded(_from);
    IFireBirdPair pair = IFireBirdPair(_from);
    address token0 = pair.token0();
    address token1 = pair.token1();
    bool isfireBirdPair = fireBirdFactory.isPair(_from);
    if (token0 == WBNB || token1 == WBNB) {
        if (isfireBirdPair) {
            (amountA, amountB) = fireBirdRouter.removeLiquidityETH(_from, token0 != WBNB ? token0 : token1, amount, 1, 1, msg.sender, block.timestamp);
        } else {
            (amountA, amountB) = uniRouter.removeLiquidityETH(token0 != WBNB ? token0 : token1, amount, 1, 1, msg.sender, block.timestamp);
        }
    } else {
        if (isfireBirdPair) {
            (amountA, amountB) = fireBirdRouter.removeLiquidity(_from, token0, token1, amount, 1, 1, msg.sender, block.timestamp);
        } else {
            (amountA, amountB) = uniRouter.removeLiquidity(token0, token1, amount, 1, 1, msg.sender, block.timestamp);
        }
    }
}
```

## Recommendation
Improve the above function by adding necessary slippage control with the user-specified amountAMin and amountBMin.
