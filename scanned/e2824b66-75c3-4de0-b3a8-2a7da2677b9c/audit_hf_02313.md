# [M] Non-Payable removeLiquidityETH()

## Summary
Severity: Medium
Contest weight: 0.4399
Dataset id: 12598
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the OneSwapRouter contract, there is another entry routine, i.e., removeLiquidityETH(). This routine allows the pool's liquidity providers to remove liquidity from the pool. By transparently unwrapping WETHs into ETH, removeLiquidityETH() greatly facilitates user experience for native ETHs.

It is important to note that this routine is only supposed to accept the pool's liquidity tokens, not others including ETHs. Therefore, the current definition of function removeLiquidityETH(address pair, uint liquidity, uint amountTokenMin, uint amountETHMin, address to, uint deadline) external override payable may wrongfully allow taking users' accidental ETH deposit. To prevent that from happening, it is suggested to remove the keyword payable from the definition.

```solidity
function removeLiquidityETH(address pair, uint liquidity, uint amountTokenMin, uint amountETHMin, address to, uint deadline) external override ensure(deadline) payable returns (uint amountToken, uint amountETH) {
    address token;
    (address stock, address money) = _getTokensFromPair(pair);
    if (stock == weth) {
        token = money;
        (amountETH, amountToken) = _removeLiquidity(pair, liquidity, amountETHMin, amountTokenMin, address(this));
    } else if (money == weth) {
        token = stock;
        (amountToken, amountETH) = _removeLiquidity(pair, liquidity, amountTokenMin, amountETHMin, address(this));
    } else {
        require(false, "OneSwapRouter: PAIR_MISMATCH");
    }
    IWETH(weth).withdraw(amountETH);
    _safeTransferETH(to, amountETH);
    _safeTransfer(token, to, amountToken);
}
```

## Recommendation
Remove the payable keyword from the removeLiquidityETH() definition.
