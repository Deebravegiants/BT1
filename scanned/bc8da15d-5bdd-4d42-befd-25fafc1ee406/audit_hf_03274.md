# [M] When staking on a given knot

## Summary
Severity: Medium
Contest weight: 0.2029
Dataset id: 17968
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When staking on a given knot, the protocol prevents staking amounts fewer than 1 gwei. Additionally, when unstaking, there’s a check against unstaking amounts greater than the amounts allowed (at [263](https://github.com/pvgo80/2023-01-blockswap-fv-private/blob/certora/contracts/syndicate/Syndicate.sol#L263)), but there’s no check on the remaining amount. Thus, this leaves open scenarios where the user may leave less than 1 gwei on a knot. In such cases, the user cannot claim additional earnings due to the following calls: [679](https://github.com/pvgo80/2023-01-blockswap-fv-private/blob/certora/contracts/syndicate/Syndicate.sol#L679) \- [693](https://github.com/pvgo80/2023-01-blockswap-fv-private/blob/certora/contracts/syndicate/Syndicate.sol#L693) \- [370](https://github.com/pvgo80/2023-01-blockswap-fv-private/blob/certora/contracts/syndicate/Syndicate.sol#L370).

The user could “restake” his position on a knot, but there’s a (short) limit of 12 eth that could be filled by anyone.  
A Knot could become inactive, making future rewards forever inaccessible.  
The user could recover the smalls staked amounts, but he’ll not be compensated by accrued earnings.  
Property violated.

Rule `issue2_unstakingLeavesSmallAmountsBehind` in `M002.spec`, regarding the possibility of small stakes.  
Rule `issue2_ifTheUserHasClaimableAmountsHeShouldBeAbleToClaimIt` in `M002.spec` regarding the rewards unclaimable.

## Recommendation
Prevent unstaking shares when the amount remaining is less than 1 gwei.

**vince0656 (Blockswap) commented:**  

Assessment: Low/Medium

We will remove the check on the minimum amount that must be unstaked to avoid this. Thanks.

**teryanarmen (Certora) commented:**  

I believe this is medium severity as the protocol leaks funds but major funds are not at risk.
