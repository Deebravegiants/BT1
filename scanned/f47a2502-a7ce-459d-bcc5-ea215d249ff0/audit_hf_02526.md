# [M] Minting._sortAmountsForLP() implements a high slippage percentages on the minimum accepted tokens of the liquidity position

## Summary
Severity: Medium
Contest weight: 0.5749
Dataset id: 13516
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`Minting._sortAmountsForLP()` is called to sort tokens and calculate the accepted minimum amounts when the owner of the contract adds liquidity to the inferno-phoenix Uni-v3 pool via `Minting.addLiquidityToInfernoPhoenixPool()`:
```solidity
function _sortAmountsForLP(uint256 _infernoAmount, uint256 _phoenixAmount)
    internal
    view
    returns (
        uint256 amount0,
        uint256 amount1,
        uint256 amount0Min,
        uint256 amount1Min,
    )
{
    (token0, token1) = _phoenix < _inferno ? (_phoenix, _inferno) : (_inferno, _phoenix);
    (amount0, amount1) = token0 == _phoenix ? (_phoenixAmount, _infernoAmount) : (_infernoAmount, _phoenixAmount);
    (amount0Min, amount1Min) = (wmul(amount0, uint256(0.2e18)), wmul(amount1, uint256(0.2e18)));
}
```
As can be noticed, the minimum amounts calculated as 20% of the amounts that are going to be added as a liquidity, which means accepting a 80% slippage.

In case of market volatility during liquidity addition; this would result in accepting low amounts of tokens for the created position, which will result in collecting less fees ($Phoenix & $Inferno) for that position; thus affecting the amounts of $Inferno tokens that are going to be sent to the fluxStakingVault for staking (after swapping to $Flux).

## Recommendation
```solidity
function _sortAmountsForLP(uint256 _infernoAmount, uint256 _phoenixAmount)
    internal
    view
    returns (
        uint256 amount0,
        uint256 amount1,
        uint256 amount0Min,
        uint256 amount1Min,
    )
{
    (token0, token1) = _phoenix < _inferno ? (_phoenix, _inferno) : (_inferno, _phoenix);
    (amount0, amount1) = token0 == _phoenix ? (_phoenixAmount, _infernoAmount) : (_infernoAmount, _phoenixAmount);
    (amount0Min, amount1Min) = (wmul(amount0, uint256(0.8e18)), wmul(amount1, uint256(0.8e18)));
}
```
