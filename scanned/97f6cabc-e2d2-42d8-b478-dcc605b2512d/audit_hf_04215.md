# [C] C-04 | Market Size Increased Indefinitely With Merge Accounts

## Summary
Severity: Critical
Contest weight: 0.2691
Dataset id: 21109
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function mergeAccounts can merge any 2 accounts, adding their collateral and combining their
positions. If the positions are opposite to each other the accounts will be merged with a reduced
position size, however the market size will remain the same. This enables attacker to increase the
size of the market as much as they want, while paying only order fees.
The impact from this is complex as size is taken into quite a few calculations and checks:
1. Increasing size increases utilization lowering PnL for other users.
2. Increasing size will reach max OI, which will prevent users from opening trades.
3. Utilizing 100% of the market will cause the LPs to be locked, as delegateCollateral will revert,
which leads to minimumCredit checking if we are over the limit.
delegateCollateral -> _verifyNotCapacityLocked -> findMarketWithCapacityLocked ->
isCapacityLocked -> getLockedCreditCapacity -> minimumCredit
Note that this doesn't need to be "exploited", as it will occur naturally with use of the protocol.

## Proof of Concept
https://github.com/GuardianAudits/synthetix-pocs/blob/main/markets/bfp-market/test/integration/modules/team2PoCs.test.ts#L231

## Recommendation
Check if the two positions are different and if true update the market size.
