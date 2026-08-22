# [M] The WETH arbitrage profits that are not swapped to SALT will be stuck in `Pools`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-08
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/123
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/6998661013e86a50c7db552d189fadb0521dbeb0/src/pools/Pools.sol#L306-L307


# Vulnerability details

# Mitigation
[commit 6998661](https://github.com/othernet-global/salty-io/commit/6998661013e86a50c7db552d189fadb0521dbeb0)
In the pervious implementation, the WETH arbitrage profits will be swapped to SALT immediately in `_arbitrage()` function. However, it could fail if there is no SALT/WETH liquidity in `Pools`.
The mitigation skipped the swapping step if there is no SALT/WETH liquidity.

# Vulnerability details
The WETH arbitrage profits were not swapped to SALT because the mitigation skipped the swapping step under zero SALT/WETH liquidity. However, it doesn't record this for future swapping. As a result, all WETH arbitrage profits obtained under zero SALT/WETH liquidity will be stuck in Pools.

# Tools Used
Manual review
### Recommended Mitigation Steps
Introduce a variable to accumulate the unswapped arbitrage profits and attempt to swap them for SALT next time.









## Assessed type

Other
