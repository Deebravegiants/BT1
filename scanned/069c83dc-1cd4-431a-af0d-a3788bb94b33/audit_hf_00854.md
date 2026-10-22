# [M] M-14 | burnSynthsToTarget Functionality Changes

## Summary
Severity: Medium
Contest weight: 0.1177
Dataset id: 2591
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to [SCCP-2134: LegacyMarket V3 Migration Preparations](https://github.com/Synthetixio/SIPs/blob/master/content/sccp/sccp-2134.md), issuanceRatio will be settled to 1 wei. When issuanceRatio became 1 wei, maxIssuableSynths will be in the orders of wei for every user. This will lead to burnSynthsToTarget function to leave its' normal functionality (which is burning to the c-ratio), and instead burn all debt user has. Considering self-liquidations are disabled and right now it was announced to users that they need to burn back to c-ratio in order to avoid an automated liquidation, a lot of users might use burnSynthsToTarget function to burn to the c-ratio. But with issuanceRatio change, they will encounter a result that they weren't expecting.

## Recommendation
Inform users about this following change in burnSynthsToTarget so that they encounter not expected burns.
