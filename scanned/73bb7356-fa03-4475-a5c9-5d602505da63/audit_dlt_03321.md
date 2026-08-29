# [H] DoS for submitting batches and logic calls

## Summary
Severity: High
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-08
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/24
Type: code-finding

## Details
# Handle

0xito


# Vulnerability details

## Impact
when `submitbatch` is called with a `_batchnonce` of the maximum unsigned number (`type(uint256).max`), all future calls will fail due to this check:

```
require(state_lastBatchNonces[_tokenContract] = type(uint256).max < _batchNonce, "...");
```

no batches can be submitted again but are still accepted on the cosmos side.

The same issue exists for `submitLogicCall` and setting `args.invalidationNonce = type(uint256).max`

## Proof of Concept

## Tools Used

## Recommended Mitigation Steps
the nonces should not be arbitrary, ideally, they are the previous nonce + 1, or within a range of the previous nonce.
