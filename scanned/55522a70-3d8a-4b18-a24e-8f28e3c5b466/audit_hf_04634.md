# [M] LibUbiquityPool::mintDollar/redeemDollar re-

## Summary
Severity: Medium
Contest weight: 0.1419
Dataset id: 22373
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ubiquity pool used for minting/burning uAD relies on a twap oracle which can be outdated because the underlying metapool is not updated when calling the ubiquity pool. This would mean that minting/burning will be enabled based on an outdated state when it should have been reverted and inversely.

We can see that LibTWAPOracle has an update function to keep its values up to date according to the underlying metapool:
kages/contracts/src/dollar/libraries/LibTWAPOracle.sol#L61-L102

And that this function is called when minting/burning uADs:
kages/contracts/src/dollar/libraries/LibUbiquityPool.sol#L344
kages/contracts/src/dollar/libraries/LibUbiquityPool.sol#L416

But the function update is not called on the underlying metapool, so current values fetched for it may be stale:
kages/contracts/src/dollar/libraries/LibTWAPOracle.sol#L134-L136

A malicious user can use this to mint/burn heavily in order to depeg the coin further.

## Recommendation
Call the function: On the underlying metapool the twap is based on, with only zero values, to ensure that the values of the pool are up to date when consulted.
