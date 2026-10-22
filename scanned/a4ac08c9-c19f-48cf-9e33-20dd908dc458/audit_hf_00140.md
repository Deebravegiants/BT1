# [M] Possible locked-ether

## Summary
Severity: Medium
Contest weight: 0.1406
Dataset id: 535
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When running the analyzer code, the following functions were found in `RCOrderbook.sol` to possibly lock funds due to it being a payable function with no withdraw function associated. See [Issue #43](https://github.com/code-423n4/2021-06-realitycards-findings/issues/43) for more details.

I initially confirmed this because we aren’t using the native currency on Matic/Polygon. However I think this should be disputed mainly because this function is used to call other functions which might be payable, although I admit currently we don’t have payable functions, we might add them in the future. This library is used across all our contracts, had we put a payable function in the Treasury for instance, would this be considered a flaw to have this same library imported into the Orderbook?

Note that the duplicate issue #51 was submitted by the same user.

Agree with the sponsor’s explanation, but the issue exists regardless. Adding a way to retrieve locked funds would mitigate the issue.

## Recommendation
No recommendation
