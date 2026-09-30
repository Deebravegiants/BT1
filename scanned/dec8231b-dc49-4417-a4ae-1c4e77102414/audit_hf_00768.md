# [M] M-01 | Incorrect Gas Estimation

## Summary
Severity: Medium
Contest weight: 0.4619
Dataset id: 2394
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMX estimates the execution fee for sponsored calls using the following formula:
```solidity
// Multiply calldataLength by 2 because the calldata is first sent to the Relay contract, and then to GMX contract
// Zero byte in calldata costs 4 gas, non-zero byte costs 16 gas; use 12 as a conservative average
uint256 l2Fee = (relayFeeBaseAmount + calldataLength * 2 * 12 + startingGas - gasleft()) * tx.gasprice;
```
Here, calldataLength * 2 * 12 is used to estimate the calldata cost. The factor of 2 is intended to account for the calldata being sent first to the Relay contract and then to GMX. The average gas cost per byte is assumed to be 12, considering zero and non-zero bytes (4 and 16 gas respectively), which is a reasonable approximation for [transaction creation](https://github.com/wolflo/evm-opcodes/blob/main/gas.md#a0-0-intrinsic-gas), where this cost is intrinsic and paid upfront before opcode execution.

However, this assumption does not hold for external calls made on-chain (i.e., from the Relay contract to GMX). In external contract calls, calldata is not charged the same way as in transaction creation. Instead, the calldata is copied to memory, and memory expansion costs must be considered. The CALL opcode takes memory offset and size as stack arguments for this reason.

Key references:
• [EVM Opcodes – CALL](https://www.evm.codes/?fork=cancun#f1)
• [External call gas breakdown](https://github.com/wolflo/evm-opcodes/blob/main/gas.md#aa-call-operations)
• [Memory expansion (quadratic cost)](https://github.com/wolflo/evm-opcodes/blob/main/gas.md#a0-1-memory-expansion)

Unlike the linear estimation 12 * calldataLength, memory expansion cost is quadratic in nature. This makes GMX’s fee estimation potentially inaccurate.

Specifically:
• GMX may underestimate the l2Fee when calldata is large (potentially exposing GMX to a loss),
• And overestimate it when calldata is small, making users repay more than necessary.

For a visual comparison of the gas cost growth curves, refer to this graph:
[Desmos graph – Linear vs. Memory Expansion](https://www.desmos.com/calculator/kcxwbnf6wn)
• For smaller calldata lengths, the linear approximation (12 * calldataLength) overestimates the actual memory cost.
• At a certain point, memory expansion begins to drastically outpace the linear estimation.

In theory, an attacker could exploit this by submitting a transaction with a large enough calldata payload, causing the actual memory expansion cost to significantly exceed the estimated fee—leading to GMX covering the shortfall. However, this is unlikely in practice due to the following:
• The intersection point where memory expansion overtakes the linear estimate is around 75 million gas, which is far beyond the current block gas limit. Hence, the worst impact in this case is users paying more to GMX than they should.

## Recommendation
Consider removing the "twice" multiplier and approximating the gas cost for memory expansion. Also, include the gas overhead of 700 in the base cost, as that is the base cost for the CALL opcode.
