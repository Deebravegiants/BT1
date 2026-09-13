# [H] Use of `isOutdated`

## Summary
Severity: High
Source: https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/oracle/IOracle.sol
Type: audit-issue

## Details
All oracles of type [IOracle](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/oracle/IOracle.sol) implement a [function isOutdated](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/oracle/IOracle.sol#L21) which signals whether or not the current oracle price is outdated. This function is [utilized in PCVSwapperUniswap](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/pcv/PCVSwapperUniswap.sol#L185), however the rest of the codebase ignores the function, and never checks whether an oracle needs to be updated.
