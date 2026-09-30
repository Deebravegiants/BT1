# [H] OptionTokenV4.exerciseLP's addLiquidity lack slippage protection

## Summary
Severity: High
Contest weight: 0.7859
Dataset id: 23117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
an exercise operation, as well as due to the pool being imbalanced, the depositor can receive less liquidity than intended, burning more OptionTokens for less LP tokens
80eff4bd12578146a844cfd/v4-contracts/contracts/OptionTokenV4.sol#L690-L70
here to see the gain when
```solidity
underlyingToken,
paymentToken,
false,
_amount,
paymentAmountToAddLiquidity,
1,
1,
address(this),
block.timestamp
);
```
OptionTokenV4.exerciseLP has a slippage check on the maximum price paid to exercise the option. But there is no check that the lpAmount is within the bounds of what the user intended.
The Pool.mint formula for liquidity to be minted is as follows:
80eff4bd12578146a844cfd/v4-contracts/contracts/Pair.sol#L262-L263
```solidity
liquidity = Math.min(_amount0 * _totalSupply / _reserve0, _amount1 * _totalSupply / _reserve1);
```
To calculate the correct amount of paymentReserve to add to the pool, spot reserves are checked
80eff4bd12578146a844cfd/v4-contracts/contracts/OptionTokenV4.sol#L354-L35
```solidity
(uint256 underlyingReserve, uint256 paymentReserve) = IRouter(router).getReserves(underlyingToken, paymentToken, false);
```
```solidity
paymentAmountToAddLiquidity = (_amount * paymentReserve) / underlyingReserve;
```
This means that spot reserves are read and are supplied in a proportional way, this is rational and superficially correct. liquidity we will get is directly related to how "imbalanced the pool is".
When a pool is perfectly balance (e.g. both reserves are in the same proportion), we will have the following math:
Start balances tokenA: 1000000000000000000 (1e18) tokenB: 1000000000000000000 (1e18)
New Deposit: 1000000000000000000 (1e18) New tokens minted: 1000000000000000000 (1e18)
Meaning we get a proportional amount.
However, if we start imbalancing the pool by adding more underlyingToken, then the amount of paymentAmountToAddLiquidity will be reduced, meaning we will be using the same _amount of underlying but we will receive less total LP tokens. This can happen naturally, if the pool is imbalanced and can also be exploited by an attacker to cause the ExerciseLP to be less effective than intended. Less LP tokens will be produced from burning the OptionTokens, resulting in a loss of the value of the OptionToken.

## Recommendation
Add an additional slippage check for exerciseLP to check that lpAmount is above a slippage threshold.
