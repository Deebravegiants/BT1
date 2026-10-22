# [M] Logic Error Of addLiquidityAVAX()

## Summary
Severity: Medium
Contest weight: 0.4620
Dataset id: 12291
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
HurricaneSwap on Avalanche is designed as an evolutional improvement of UniswapV2, which is a major decentralized exchange (DEX) running on top of the Ethereum blockchain. HurricaneSwap follows UniswapV2's core design, but extends with restricted tokens feature. If both of the tokens in the pool are restricted, only the privileged owner account can continue to add or remove liquidity for the pool. To elaborate, we show below the related code snippet of the AvaxHurricaneRouter contract. Both of the addLiquidity() and addLiquidityAVAX() functions are used by liquidity providers to add liquidity for the pool. If one of the underlying assets that the user provides is AVAX, the addLiquidityAVAX() function will be used, otherwise the addLiquidity() function will be used. In the addLiquidity() function, we notice that only the privileged owner account can continue to add liquidity for the pool if both of the tokens in the pool are restricted (line 69 - line 77). However, it comes to our attention that the addLiquidityAVAX() function does not have the same logic. We may intend to keep consistency between the addLiquidity() and addLiquidityAVAX() functions.
```solidity
function addLiquidity(
    address tokenA,
    address tokenB,
    uint amountADesired,
    uint amountBDesired,
    uint amountAMin,
    uint amountBMin,
    address to,
    uint deadline
) external ensure(deadline) returns (uint amountA, uint amountB, uint liquidity) {
    bool hasA = IHurricaneFactory(factory).restrictedTokens(tokenA);
    bool hasB = IHurricaneFactory(factory).restrictedTokens(tokenB);
    if (hasA && hasB) {
        (bool lpSwitch, bool swapSwitch) = IHurricaneFactory(factory).getSwitch();
        require(lpSwitch && !swapSwitch, "Hurricane: liquidity closed or swap open");
        require(msg.sender == IHurricaneFactory(factory).getOwner(), "Hurricane: not allowed");
    }
    (amountA, amountB) = _addLiquidity(tokenA, tokenB, amountADesired, amountBDesired, amountAMin, amountBMin);
    address pair = AvaxHurricaneLibrary.pairFor(factory, tokenA, tokenB);
    TransferHelper.safeTransferFrom(tokenA, msg.sender, pair, amountA);
    TransferHelper.safeTransferFrom(tokenB, msg.sender, pair, amountB);
    liquidity = IHurricanePair(pair).mint(to);
    // AddLiquidity (address pair , address tokenA , address tokenB , uint tokenADesired ,
    // uint tokenBDesired , uint tokenAmin , uint tokenBmin , uint lpAmount , string method);
    emit AddLiquidity(pair, tokenA, tokenB, amountADesired, amountBDesired, amountAMin, amountBMin, liquidity, "addLiquidity");
    // emit Method( addLiquidity );
}

function addLiquidityAVAX(
    address token,
    uint amountTokenDesired,
    uint amountTokenMin,
    uint amountAVAXMin,
    address to,
    uint deadline
) external payable returns (uint amountToken, uint amountAVAX, uint liquidity) {
    require(deadline >= block.timestamp, "HurricaneRouter: EXPIRED");
    (amountToken, amountAVAX) = _addLiquidity(
        token,
        WAVAX,
        amountTokenDesired,
        msg.value,
        amountTokenMin,
        amountAVAXMin
    );
    address pair = AvaxHurricaneLibrary.pairFor(factory, token, WAVAX);
    TransferHelper.safeTransferFrom(token, msg.sender, pair, amountToken);
    IWAVAX(WAVAX).deposit{value: amountAVAX}();
    assert(IWAVAX(WAVAX).transfer(pair, amountAVAX));
    liquidity = IHurricanePair(pair).mint(to);
    // refund dust AVAX, if any
    if (msg.value > amountAVAX) TransferHelper.safeTransferAVAX(msg.sender, msg.value - amountAVAX);
    emit AddLiquidity(pair, token, WAVAX, amountTokenDesired, msg.value, amountTokenMin, amountAVAXMin, liquidity, "addLiquidityAVAX");
    // emit Method( addLiquidityAVAX );
}
```

## Recommendation
Validate whether both of the tokens in the pool are restricted at the beginning of the addLiquidityAVAX() function. If so, only the privileged owner account can continue to add liquidity for the pool.
