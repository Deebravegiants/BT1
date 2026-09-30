# [M] Validator signatures with greater timestamps can be reused in a subsequent updateCollateral

## Summary
Severity: Medium
Contest weight: 0.1492
Dataset id: 10699
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling MinterGateway.updateCollateral, an array of timestamps gets passed. That is because the digest signed by a validator includes an updating timestamp. The minimum timestamp between the signatures will be used as the new collateral update timestamp. This is used to check for staleness, which also has the side effect of preventing replaying a set of signatures. Provided the collateral amount stays the same, all signatures with a timestamp larger than the minimum timestamp between them can be reused for a subsequent update. This means that the minter may just need to get a signature from one validator and use all others. The new updateTimestamp may not be as large as if the minter had requested new signatures from all validators, but it still can allow the minter to delay the penalization time. Potentially, they can even misrepresent their on-chain collateral value during a small period, provided there's one malicious validator willing to forge a signature.

## Recommendation
A gas-intensive solution would be to flag each new digest as used in storage. A less intensive mitigation would be to explicitly prevent a large deviation of the timestamps being used in an updateCollateral call.
