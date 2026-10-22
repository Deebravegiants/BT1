# [M] M-3 Truncation of the nonce value

## Summary
Severity: Medium
Contest weight: 0.0885
Dataset id: 3661
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the BebopSigning.sol#L167 function, a uint256 value is cast to uint64, silently ignoring higher bits of the value. This could lead to value collisions when different nonce values as uint256 have the same values as uint64. Although the uint64 value range is generally sufﬁcient for the purpose of a nonce, and a nonce collision would likely cause a revert and, thus, it doesn't seem to be exploitable, the code's security could be further enhanced by addressing this issue.

## Recommendation
It's recommended to utilize as many bits of the value as possible (248 bits seems to be a reasonable approach for this code). Additionally, it's recommended to ensure that the truncated bits of the value were actually zero to prevent value collisions.
