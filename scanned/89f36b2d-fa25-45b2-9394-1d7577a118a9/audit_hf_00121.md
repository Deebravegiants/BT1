# [M] Legacy Function Usage

## Summary
Severity: Medium
Contest weight: 0.0756
Dataset id: 298
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `withdraw` function utilizes the `transfer` invocation, which has a fixed gas stipend and can fail, especially beyond the Berlin fork, which increased the [gas costs](https://eips.ethereum.org/EIPS/eip-2929) for first-time invocations of a transfer.

The EIP should be sufficient.

Recommend using a safe wrapper library, such as the OpenZeppelin `Address` library’s `sendValue` function, which forwards sufficient gas for the transfer regardless of the underlying OPCODE gas costs.

## Recommendation
No recommendation
