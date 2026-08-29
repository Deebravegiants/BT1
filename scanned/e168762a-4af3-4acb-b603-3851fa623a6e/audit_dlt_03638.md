# [M] An attacker can DOS AutoExit and AutoRange transformers and incur losses for position owners

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-28
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/66
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/dcfa79924c0e0ba009b21697e5d42d938ad9e5e3/src/automators/AutoExit.sol#L130
https://github.com/revert-finance/lend/blob/dcfa79924c0e0ba009b21697e5d42d938ad9e5e3/src/transformers/AutoRange.sol#L139


# Vulnerability details

## Impact

An exploiter can block the execution of AutoExit and AutoRange transformers, which leads to the following consequences:
- `Limit orders` & `Stoploss orders` - position owners won't be able to exit a bad market and will suffer losses
- `Autorange orders` - positions that go out-of-range won't be rebalanced leading to missed profits or direct losses
 
## Vulnerability details

The `AutoRange.sol` and `AutoExit.sol` contracts serve the following functionality in Revert Lend:

- [`AutoRange.sol` contract](https://docs.revert.finance/revert/auto-range)
> Auto-Range automates the process of rebalancing your liquidity positions. When the token price moves and your position goes out-of-range by your selected percentage, the system then automatically rebalances your position`

- [`AutoExit` contract](https://docs.revert.finance/revert/auto-exit)
> Auto-Exit lets you pre-configure a position so that the liquidity is automatically withdrawn when the pool price reaches a predetermined value. Moreover, you can optionally configure the system to swap from one token to the other on withdrawal, providing a safety net for your investments akin to a stop-loss order.

Both of those contracts implement an `execute()` function that respectively transforms an NFT position based on the parameters provided to it. It can only be called by revert controlled bots (operators) which owners have approved for their position or by the `V3Vault` through it's `transform()` function.

The problem in both of those contracts is that the `execute()` function includes a validation that allows malicious users to DOS transaction execution and thus compromise the safety and integrity of the managed positions.

`AutoExit::execute()`

https://github.com/revert-finance/lend/blob/audit/src/automators/AutoExit.sol#L130
```solidity
 function execute(ExecuteParams calldata params) external {
        ....       
 
        // get position info
        (,, state.token0, state.token1, state.fee, state.tickLower, state.tickUpper, state.liquidity,,,,) =
            nonfungiblePositionManager.positions(params.tokenId);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/66_
