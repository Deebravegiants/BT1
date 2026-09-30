# [M] Admin privileges are dangerous

## Summary
Severity: Medium
Contest weight: 0.0781
Dataset id: 3363
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious or a compromised admin can execute a 100% rug pull in the following way:
1. The LP admin calls the Factory contract to add a malicious core to the LP
2. The malicious core returns the LP contract balance when its resolveAffiliateReward method is called
3. Now calling claimAffiliateReward with the fake core as an argument will result in a 100% of the LP balance stolen
Same thing applies to withdrawPayout .

## Recommendation
Make the process of adding a new coreType or calling plugCore to be safer. One possible approach is by adding a time delay before a core is added to the LP , up until which the request will be pending.
