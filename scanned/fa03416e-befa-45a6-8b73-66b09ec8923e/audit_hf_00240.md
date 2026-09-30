# [M] `BasePool.mint

## Summary
Severity: Medium
Contest weight: 0.1294
Dataset id: 1242
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `BasePool.mint()` function differs from its implementation in `BasePoolV2.mint()` in which it lacks an `onlyRouter` modifier. This ensures that users cannot call this function directly as `VaderRouter.addLiquidity()` performs some necessary input validation which can be bypassed by directly calling `BasePool.mint()`.

## Proof of Concept
* <https://github.com/code-423n4/2021-11-vader/blob/main/contracts/dex/router/VaderRouter.sol#L123-L150>
* <https://github.com/code-423n4/2021-11-vader/blob/main/contracts/dex/pool/BasePool.sol#L149-L194>

## Recommendation
Consider adding an `onlyRouter` modifier to the `BasePool.mint()` function to ensure users cannot directly call this function.

The pool contracts, similarly to Uniswap V2, are never meant to be interacted with directly.

That’s what the modifier would do.

They are never meant however it should still be possible to do so. With Uniswap V2, it is possible to interact with the contracts directly however doing so (without using a smart contract) will result in the same vulnerabilities as described in the issue. This is not intended usage and as such does not constitute an issue unless it is implied that the Uniswap V2 implementation is incorrect.
