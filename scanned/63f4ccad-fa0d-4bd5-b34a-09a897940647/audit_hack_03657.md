# [M] Usage of transfer function without checking return value can result in failure to rescue ERC20 tokens

## Summary
Severity: Medium
Reporter: aphak5010
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L95
Type: audit-issue

## Details
# Usage of transfer function without checking return value can result in failure to rescue ERC20 tokens

## Summary
In the `FeeBuyBack` contract are 3 instances where `transfer` / `transferFrom` is used without checking the return value.
For two of the instances this is not a problem since a failure to transfer funds will cause a revert in the remaining function code.
However in the `FeeBuyBack.rescueERC20` function the `transfer` function might fail and the `rescueERC20` function will still return `true`.

## Vulnerability Detail
The vulnerable code: [https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L95](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L95)

## Impact
The `rescueERC20` function can only be called by the owner of the contract.
The owner of the contract can itself be a contract which might rely on the `rescueERC20` to only return `true` if the transfer is successful. Failure to do so might result in a loss of funds.
For example the owner contract might only allow rescuing tokens once and will think everything's ok when the `rescueERC20` function returns `true`.

## Code Snippet
[https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L95](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L95)

## Tool used
Manual Review

## Recommendation
Import the SafeERC20 library from OpenZeppelin and replace `transfer` / `transferFrom` with `safeTransfer` / `safeTransferFrom`.
