# [H] Inverting oracle prices

## Summary
Severity: High
Source: https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/pcv/PCVSwapperUniswap.sol#L36
Type: audit-issue

## Details
Oracles return a price of a currency X, in terms of a currency Y, which can then be inverted if what is desired is the price of Y in terms of X. However the possibilities of inverting token prices is inconsistent throughout the codebase. The [PCVSwapperUniswap has a boolean flag invertOraclePrice](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/pcv/PCVSwapperUniswap.sol#L36) which signals whether the oracle being used needs to be inverted or not, whereas the [ReserveStabilizer always inverts the price](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/stabilizer/ReserveStabilizer.sol#L58), and the remainder of the codebase never inverts the price.

Consider updating the codebase to remove the above inconsistencies and vulnerabilities, and updating all comments and documentation to reflect the intended use of all functions and booleans.

_**Update:** Partially fixed in [PR#69](https://github.com/fei-protocol/fei-protocol-core-internal/pull/69). The implementations of updating and inverting oracle prices have been fixed in this PR. The PR additionally makes the use of `isOutdated` consistent throughout the codebase – the function is now not used at all. However, given that the purpose of `isOutdated` is to flag whether an oracle price is stale, reading oracle prices without first calling `isOutdated` could lead to incorrect prices being used throughout the protocol to determine critical conditions._
