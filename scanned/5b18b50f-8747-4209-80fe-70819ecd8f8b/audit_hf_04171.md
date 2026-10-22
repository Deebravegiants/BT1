# [H] H-05 | Native Yield Token Yields Cannot Be Conﬁgured After Deployment

## Summary
Severity: High
Contest weight: 0.1668
Dataset id: 20852
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the IERC20Rebasing interface the conﬁgure function is deﬁned to return a YieldMode enum value. However the actual native yield precompiles will return a uint256 representing the balance of the user: ERC20Rebasing. As a result any call to the BlastYields.enableTokenClaimable function will fail when the contract’s balance is nonzero (or above 2 wei) as the result will not correctly correspond to an enum value. Therefore the conﬁguration cannot be updated after deployment, or deployment could even be prevented if a malicious actor sends a few wei of the native yield token to the target address.

## Recommendation
Correct the IERC20Rebasing interface to return a uint256 value from the conﬁgure function rather than a YieldMode enum value.
