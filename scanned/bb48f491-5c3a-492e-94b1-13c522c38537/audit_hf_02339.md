# [M] Proper pSharePerSecond Calculation in PShareRewardPool

## Summary
Severity: Medium
Contest weight: 0.4166
Dataset id: 12705
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the Pegasus Dollar protocol, there is a PShareRewardPool contract that shares a MasterChef-like design to disseminate the pShare tokens. While analyzing this contract, we notice the pSharePerSecond parameter needs to be revisited. To elaborate, we show below the key storage states defined in the PShareRewardPool contract. It comes to our attention that the pSharePerSecond state is initialized as pSharePerSecond = 0.00221968543 ether, which is derived from the following formula: 70000 pshare / (354 days * 24h * 60min * 60s) = 0.00221968543 ether. However, the runningTime parameter is defined as the 1000 days, not the 354 days used for the pSharePerSecond calculation! In fact, if we use the 1000 days as the runningTime, the computed pSharePerSecond should be 0.000810185185185 ether!
```solidity
// The time when PShare mining ends.
uint256 public poolEndTime;
uint256 public lastTimeUpdateRewardRate;
uint256 public accumulatedRewardPaid;
uint256 public pSharePerSecond = 0.00221968543 ether; // 70000 pshare / (354 days * 24h * 60min * 60s)
uint256 public runningTime = 1000 days;
uint256 public constant TOTAL_REWARDS = 70000 ether;
```

## Recommendation
Properly initialize the pSharePerSecond state. Result The issue has been fixed by this commit: dd9fa0f.
