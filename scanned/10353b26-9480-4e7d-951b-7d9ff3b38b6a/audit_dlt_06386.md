# [M] Oracle functions can revert due to vulnerable implementations of Uniswap libraries

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-08
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/3
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xe0e09f38d16ea0e9202aa62cbca677b33fc61b61006f79b3ea7c1f674c4a312c
**Severity:** medium

**Description:**
## Impact
Oracle getter functions can revert ocassionally.

## Execution traces
- `PendleTokenCustomOracle.sol` - `latestAnswer()` -> `OracleLibrary` - `getQuoteAtTick()`
- `WiseOracleHub.sol` - `latestResolverTwap()` -> `OracleHelper.sol` - `_getTwapPrice()` & `_getTwapDerivatePrice()` -> `OracleLibrary` - `getQuoteAtTick()`

Vulnerable functions use the underlying `OracleLibrary` or `FullMath` / `TickMath`.

## Description
In the `TickMath` and `FullMath`  libraries an overflow is desired, however it's never reached because the libraries doesn't correctly handle the case when a value overflows 256 bits. The libraries was likely taken from the Uniswap V3  [core](https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/TickMath.sol)  and  [periphery](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol)  repositories and updated to solidity version 0.8.24 which reverts on overflow. However the solidity version used here is important because the the original repositories used < 0.8.0 and execution didn't revert when an overflow was reached. This means when an overflow occurs the execution will revert and the correct result won't be returned. The original uniswap libraries were designed in a way that desire and handle overflows.

## Recommendation

Consider to wrap all  `TickMath`, `Fullmath` and `OracleLibrary` functions in an unchecked block. For reference you can check out the official Uniswap 0.8 branch which uses `unchecked` blocks for every function: [`Uniswap/v3-core/blob/0.8/contracts/libraries/TickMath.sol`](https://github.com/Uniswap/v3-core/blob/0.8/contracts/libraries/TickMath.sol).

## Other References:

-   [Overlay - Spearbit - High](https://solodit.xyz/issues/use-unchecked-intickmathsol-andfullmathsol-spearbit-overlay-pdf)
-   [Timeless - Spearbit - Medium](https://solodit.xyz/issues/tickmath-might-revert-in-solidity-version-08-spearbit-timeless-pdf)
-   [TapiocaDAO - code4rena - Medium](https://github.com/code-423n4/2023-07-tapioca-findings/issues/483)
