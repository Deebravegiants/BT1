# [M] lpFeesTotal is not reset to 0

## Summary
Severity: Medium
Contest weight: 0.5607
Dataset id: 5534
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LP fees is not reset after distribution. This causes User/LP to get more funds than expected.
Impact Explanation:
1. If not corrected, duplicate lpFeesTotal can be claimed by User pool in all future cycles until lpPoolTotal = 0.
2. Even when LP actually deposits, the first cycle will give more fees to LP.
3. User wont be able to claim winning as protocol will lack funds.

## Proof of Concept
1. Observe the distributeLpFeesToLps function:
```solidity
function distributeLpFeesToLps() private {
    if (lpPoolTotal == 0) {
        // if no LPs have staked, distribute LP fees to the user pool
        userPoolTotal += lpFeesTotal;
        return;
    }
    // ...
    // set LpFeesTotal to 0 after distributing fees to LPs
    lpFeesTotal = 0;
```
2. As we can see if lpPoolTotal == 0 then lpFeesTotal is not reset to 0.

## Recommendation
lpFeesTotal should be set to 0 even when lpPoolTotal == 0.
```solidity
if (lpPoolTotal == 0) {
    // if no LPs have staked, distribute LP fees to the user pool
    userPoolTotal += lpFeesTotal;
    lpFeesTotal = 0;
    return;
}
```
