# [H] Missing/wrong implementation

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Examples

1. The `UniProxy` contract has different functions used for setting the properties of a position. However, `Position.priceThreshold`, and `Position.depositOverride` are never assigned to, even though they are being used.

2. `UniProxy.deposit` is calling `IHypervisor.deposit` multiple times with different function signatures (3 and 4 parameters), while the `Hypervisor` contract only implements the version with 4 parameters, and does not implement the `IHypervisor` interface.

3. `Hypervisor.uniswapV3MintCallback | uniswapV3SwapCallback` - both these functions contain unreachable code, namely  the case where `payer != address(this)`.


#### Recommendations

1. Consider adding functions to set these properties, or alternatively, a single function to set the properties of a position.
2. Consider supporting a single `deposit` function for `IHypervisor`, and make sure that the actual implementation adheres to this interface.
3. Consider deleting these lines.
