# [M] contract with only IOptimismMintableERC20 in-

## Summary
Severity: Medium
Contest weight: 0.1572
Dataset id: 19746
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a custom contract implements only the IOptimismMintableERC20, but no the ILegacyMintableERC20, the contract is not compatible with the StandardBridge, as the bridge uses the l1Token function from the legacy interface implementation of OptimismMintableERC20 using the interface IOptimismMintableERC20.

Also, the StandardBridge, which uses the OptimismMintableERC20 has _isOptimismMintableERC20 function, which checks whether the given token address is implementing OptimismMintableERC20. The function will be true if either of token implements only one of the interfaces, it will return true.

However, if the given token passes the _isOptimismMintableERC20, the legacy function l1Token will be called on the token. If the token does not implement the legacy interface, the call will fail.

Therefore, the token which only implements IOptimismMintableERC20, but not the ILegacyMintableERC20, is not compatible with StandardBridge.

Any custom contract without l1Token function will not be compatible with StandardBridge

## Recommendation
It is unclear it is intended behavior. If the _isOptimismMintableERC20 function checks whether a token implements IOptimismMintableERC20 and ILegacyMintableERC20 both, the IOptimismMintableERC20 will be treated as if they are not the optimism mintable function, without failing.
