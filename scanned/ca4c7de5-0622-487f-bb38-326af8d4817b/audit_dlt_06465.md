# [M] Issue M-21 from Code4rena audit not correctly fixed

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca
Published: 2024-05-28
Source: https://github.com/hats-finance/Tapioca-0xe0b920d38a0900af3bab7ff0ca0af554129f54ad/issues/19
Type: hats-finding

## Details
**Github username:** @bauchibred
**Twitter username:** bauchibred
**Submission hash (on-chain):** 0xcf89c2eb7afa8d2b055ba3b314bb5359193694c4fc289f7828911efec425992f
**Severity:** medium

**Description:**
**Description**

See [link](https://github.com/code-423n4/2024-02-tapioca-findings/issues/97).

This was probably missed as it was previously duplicated to a different issue.

Take a look at  https://github.com/hats-finance/Tapioca-0xe0b920d38a0900af3bab7ff0ca0af554129f54ad/blob/5da08b3d97da6d1989d73892ccabfe7438ae8a9d/contracts/governance/twTAP.sol#L626C1-L632C1
```
        // Remove participation
        if (position.hasVotingPower) {
            TWAMLPool memory pool = twAML;
            unchecked {
                --pool.totalParticipants;
            }

```

The above snippet is from the function `twTAP._releaseTap()` which updates only `--twAML.totalParticipants` and neglects to update `twAML.averageMagnitude`. This will result in twAML.averageMagnitude accumulating every time a new position participates, without ever decreasing.



**Attack Scenario**
> TLDR of the report is that an attacker can monopolize the governance by precisely controlling the number of tokens entering and exiting to ensure only their position remains in the current twTap. Additionally, if `pool.cumulative` is less than `pool.averageMagnitude`, it will be set to 0, but `position.averageMagnitude` will be added to `pool.cumulative` upon exit, causing it to continuously increase. This results in the twTAP/TapiocaOptionBroker's efficiency decreasing, as their multiplier or target will always be at the minimum value. The same issue exists in the TapiocaOptionBroker, but `pool.cumulative` will reset to `EPOCH_DURATION` instead of zero. This problem can be observed in the twTap exploit case.
**Recommendation**
Apply the fix as was suggested in [M-21](https://github.com/code-423n4/2024-02-tapioca-findings/issues/97), i.e update both the values for  `--twAML.totalParticipants` and  `twAML.averageMagnitude` in `releaseTwap()`.
**Attachments**

1. **Proof of Concept (PoC) File**

See [link](https://github.com/code-423n4/2024-02-tapioca-findings/issues/97) for more info.

2. **Revised Code File (Optional)**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Tapioca-0xe0b920d38a0900af3bab7ff0ca0af554129f54ad/issues/19_
