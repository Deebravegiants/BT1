# [M] Duplicate asset can be added

## Summary
Severity: Medium
Contest weight: 0.5663
Dataset id: 4690
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[ManagedIndex.sol#L35](https://github.com/code-423n4/2022-04-phuture/blob/main/contracts/ManagedIndex.sol#L35)  
[TopNMarketCapIndex.sol#L57](https://github.com/code-423n4/2022-04-phuture/blob/main/contracts/TopNMarketCapIndex.sol#L57)  
[TrackedIndex.sol#L45](https://github.com/code-423n4/2022-04-phuture/blob/main/contracts/TrackedIndex.sol#L45)  

Initialize function can be called multiple times with same asset. Calling with same asset will make duplicate entries in assets list. Any function reading assets will get impacted and would retrieve duplicate asset

## Proof of Concept
1. Observe that initialize function can be called multiple times
2. Admin calls initialize function with asset X
3. asset X gets added in assets object
4. Admin again calls initialize function with asset X
5. asset X again gets added in assets object making duplicate entries

## Recommendation
Add a check to fail if assets already contains the passed asset argument. Also add a modifier so that initialize could only be called once.

```solidity
require(!assets.contain(asset), "Asset already exists");
```

We require caller of `initialize` method to be a factory (which is non-upgradable contract), so it can’t be called twice

see:

```solidity
require(msg.sender == factory, "ManagedIndex: FORBIDDEN");
```

Given the factory contract is not supplied it makes it impossible to know these things and hence siding with the warden for the disclosure. 

” to be a factory (which is non-upgradable contract)” i.e. one can’t know this if the factory is not supplied or documented.
