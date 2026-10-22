# [M] updateStream() Is Not Payable

## Summary
Severity: Medium
Contest weight: 0.0772
Dataset id: 14564
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A sender can update a stream using the updateStream() function and deposit the associated stream token into the FuroStream contract.
The _depositToken() function optionally takes native Ether and deposits into bentoBox when the stream token is the wrapped Ether and there is sufficient balance of Ether in the contract.
However, updateStream() is not payable, hence it is not possible to deposit tokens into a stream with the WETH token while paying using native Ether.

## Recommendation
We recommend adding the payable modifier to updateStream() function.
