# [H] Uniswap V2 pair poisoning DoS vulnerability in liquidity migration

## Summary
Severity: High
Contest weight: 0.7761
Dataset id: 8768
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The HolofairToken contract contains a vulnerability in its liquidity migration process that allows denial-of-service (DoS) through require statements in Uniswap V2's liquidity calculations.
1. Pair Creation with Zero Reserves:
```solidity
address liquidityPool = IUniswapV2Factory(
    IUniswapV2Router02(dexRouter).factory()
).createPair(tokenAddr, IUniswapV2Router02(dexRouter).WETH());
```
This creates a pair with initial reserves of (0, 0) for (token, WETH).
2. Attacker Poisoning:
- Attacker sends 1 wei of WETH to the pair
- Attacker calls `sync()` updating reserves to (0, 1 wei)
3. Quoting issue:
When adding liquidity, the router calculates optimal amounts using `quote()`:
```solidity
function quote(uint amountA, uint reserveA, uint reserveB) internal pure returns (uint amountB) {
    require(amountA > 0, 'UniswapV2Library: INSUFFICIENT_AMOUNT');
    require(reserveA > 0 && reserveB > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY');
    amountB = amountA.mul(reserveB) / reserveA;
}
```
With reserves (0, 1 wei), any liquidity addition attempt will revert at this line require(reserveA > 0 && reserveB > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'); . This attack doesn't provide direct profit to the attacker but creates a griefing vector that permanently blocks the presale's progression to the trading phase. Once the pair is poisoned, the presale cannot be finished successfully, forcing users to withdraw their funds. Since no tokens are available before the liquidity migration, it is impossible to fix the poisoned pair after an attack occurs.

## Recommendation
The correct solution for this vulnerability is to bypass the Uniswap Router and interact directly with the Pair contract:
1. Transfer tokens and ETH directly to the pair: Instead of using the Router's functions which would fail, directly transfer both assets to the pair contract.
2. Call the pair's [`mint()`](https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol#L110C2-L131C6) function: After transferring both assets, call the pair's mint() function to create LP tokens correctly.
