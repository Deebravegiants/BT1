# [M] No check `transferFrom`

## Summary
Severity: Medium
Contest weight: 0.1044
Dataset id: 576
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The smart contract doesn’t check the return value of `token.transfer()` and `token.transferFrom()`, some erc20 token might not revert in case of error but return false. In the [TracerPerpetualSwaps:deposit](https://github.com/code-423n4/2021-06-tracer/blob/main/src/contracts/TracerPerpetualSwaps.sol#L151) and [Insurance:deposit](https://github.com/code-423n4/2021-06-tracer/blob/main/src/contracts/Insurance.sol#L51) this would allow a user to deposit for free. See issue page for other places.

Recommend wrapping the call into a `require()` or using openzeppelin’s [SafeERC20 library](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol).

## Recommendation
No recommendation
