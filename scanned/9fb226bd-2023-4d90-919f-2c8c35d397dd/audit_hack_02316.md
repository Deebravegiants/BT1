# [H] Oracle updates

## Summary
Severity: High
Source: https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/oracle/IOracle.sol#L15
Type: audit-issue

## Details
The functions [IOracle.update](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/oracle/IOracle.sol#L15) and [OracleRef.updateOracle](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/refs/OracleRef.sol#L53) return a boolean. However the definition of what this boolean signals is ambiguous. The `UniswapOracle` contract defines it as a signal whether an update was needed – `false` is not a failure, but instead just a signal that the oracle didn’t need to be updated. Whereas the `OracleRef` contract defines it as a signal of whether the update was _effective_ – here `false` is the signal of a failure to update the price.

This has lead to inconsistent handling of this boolean value: The [PCVSwapperUniswap.swap function reverts if false is returned](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/pcv/PCVSwapperUniswap.sol#L187), whereas the remainder of the codebase ignores the return value entirely. If the definition found within `OracleRef` is correct, functions throughout the codebase are not reverting when the update fails, which they should be.
