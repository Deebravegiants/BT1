# [M] `BasePool.swap

## Summary
Severity: Medium
Contest weight: 0.1469
Dataset id: 1243
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `BasePool.swap()` function differs from its implementation in `BasePoolV2.swap()` in which it lacks an `onlyRouter` modifier. This ensures that users cannot call this function directly as `VaderRouter._swap()` performs some necessary input validation which can be bypassed by directly calling `BasePool.swap()`.

## Proof of Concept
* <https://github.com/code-423n4/2021-11-vader/blob/main/contracts/dex/router/VaderRouter.sol#L304-L351>
* <https://github.com/code-423n4/2021-11-vader/blob/main/contracts/dex/pool/BasePool.sol#L289-L379>
* <https://github.com/code-423n4/2021-11-vader/blob/main/contracts/dex/pool/BasePool.sol#L261-L268>

## Recommendation
Consider adding an `onlyRouter` modifier to the `BasePool.swap()` functions to ensure users cannot directly call these functions.

The pool contracts, similarly to Uniswap V2, are never meant to be interacted with directly.

That’s what the modifier would do.

@alcueca They are never meant however it should still be possible to do so. With Uniswap V2, it is possible to interact with the contracts directly however doing so (without using a smart contract) will result in the same vulnerabilities as described in the issue. This is not intended usage and as such does not constitute an issue unless it is implied that the Uniswap V2 implementation is incorrect.
