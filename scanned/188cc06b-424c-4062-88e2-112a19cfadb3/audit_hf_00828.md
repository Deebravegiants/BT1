# [H] H-06 | Prevention Of convertUSD Via Bridge Migrations

## Summary
Severity: High
Contest weight: 0.1664
Dataset id: 2564
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The convertUSD function calls burnSynths in the V2 system which will revert if the minimum stake time has not passed since the last issuance event of the staker. By bridging sUSD from an L2 to the L1 chain with the legacy market as the destination address, anyone can set the last issuance event of the legacy market to the current block time and therefore DoS the convertUSD function for one week. This call can be repeated once per week which can make DOS permanent. Notice also that this same attack vector could be used to prevent users from burning to make their positions healthy.

## Recommendation
Consider setting the SETTING_MINIMUM_STAKE_TIME to zero as no more synths can be freshly issued. Otherwise specifically disallow bridges to the LegacyMarket.
