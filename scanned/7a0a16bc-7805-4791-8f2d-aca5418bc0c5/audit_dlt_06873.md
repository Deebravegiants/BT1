# [M] Duplicate asset can be added

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-04-phuture
Published: 2022-04-20
Source: https://github.com/code-423n4/2022-04-phuture-findings/issues/23
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-04-phuture/blob/main/contracts/ManagedIndex.sol#L35
https://github.com/code-423n4/2022-04-phuture/blob/main/contracts/TopNMarketCapIndex.sol#L57
https://github.com/code-423n4/2022-04-phuture/blob/main/contracts/TrackedIndex.sol#L45


# Vulnerability details

## Impact
Initialize function can be called multiple times with same asset. Calling with same asset will make duplicate entries in assets list. Any function reading assets will get impacted and would retrieve duplicate asset

## Proof of Concept
1. Observe that initialize function can be called multiple times
2. Admin calls initialize function with asset X
3. asset X gets added in assets object
4. Admin again calls initialize function with asset X
5. asset X again gets added in assets object making duplicate entries

## Recommended Mitigation Steps
Add a check to fail if assets already contains the passed asset argument. Also add a modifier so that initialize could only be called once

```
require(!assets.contain(asset), "Asset already exists");
```
