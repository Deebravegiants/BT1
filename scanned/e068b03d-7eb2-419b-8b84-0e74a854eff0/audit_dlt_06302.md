# [M] Core functions can revert due to vulnerable dependency in `SwEthOracle`

## Summary
Severity: Medium
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-01-22
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/1
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x9af3500e433169676a6521e1cfbc81e1642d410df1f995920513d90fcd005098
**Severity:** medium

**Description:**
## Impact
Even though `TickMath` and `UniswapOracleLibrary` are not in scope, they are inherited and have an impact on in scope contracts aka oracles relying on them like `SwEthOracle` that will likely revert once in a while, making core functions of the protocol unexecutable at times: `borrow()`, `repay()`, `depositCollateral()`, `withdrawCollateral()` because `_modifyPosition` execution trace uses a vulnerable function from the `TickMath` library: `getSqrtRatioAtTick()` that needs to overflow in order to function properly, but instead will revert on overflows due to an incorrect implementation.

## Execution trace
`IonPool.borrow()` -> `IonPool._modifyPosition()` -> `SpotOracle.getSpot()` -> `SwEthOracle.getPrice()` -> `TickMath.getSqrtRatioAtTick()`

## Description
In the `TickMath` library an overflow is desired, however it's never reached because the library doesn't correctly handle the case when a value overflows 256 bits. The  `TickMath` and `UniswapOracleLibrary` library was likely taken from the Uniswap V3  [core](https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/TickMath.sol) and [periphery](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol) repositories and updated to solidity version 0.8.21 which reverts on overflow. However the solidity version used here is important because the the original repositories used < 0.8.0 and execution didn't revert when an overflow was reached. This means when an overflow occurs the execution will revert and the correct result won't be returned. The original `TickMath` library was designed in a way that desires and handles overflows.

## Recommendation
Consider to wrap all `TickMath` functions in an unchecked block. For reference you can check out the official Uniswap 0.8 branch which uses `unchecked` blocks for every function: [`Uniswap/v3-core/blob/0.8/contracts/libraries/TickMath.sol`](https://github.com/Uniswap/v3-core/blob/0.8/contracts/libraries/TickMath.sol). For consistency use `unchecked` in in `UniswapOracleLibrary` as well.

## Other instances of this vulnerability:
- [Overlay - Spearbit - High](https://solodit.xyz/issues/use-unchecked-intickmathsol-andfullmathsol-spearbit-overlay-pdf)
- [Timeless - Spearbit - Medium](https://solodit.xyz/issues/tickmath-might-revert-in-solidity-version-08-spearbit-timeless-pdf)
- [TapiocaDAO - code4rena - Medium](https://github.com/code-423n4/2023-07-tapioca-findings/issues/483)
