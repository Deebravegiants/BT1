# [C] NMKT-1 | No Bids Can Be Entered

## Summary
Severity: Critical
Contest weight: 0.0825
Dataset id: 10826
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Initially, when no bids have been entered, the existing bid will have default values – address(0) as the collection and 0 for the tokenId. The zero address does not have function ownerOf, so the call to getOwner will revert. As a result, no bids can be entered.

## Recommendation
Bypass the ownership check when there are no existing bids.
