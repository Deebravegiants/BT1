# [H] H-01 | Dangerous setFundingRate Function

## Summary
Severity: High
Contest weight: 0.3306
Dataset id: 21894
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setFundingRate function allows a trusted address to assign the funding rate for the vault, however in almost any circumstance where the fundingRate is updated it will invalidate the funding accounting of the vault. For example: • fundingRate is 10% per year • Position A is opened at year 0 with X collateral • Position B is opened at year 1 with X collateral • The vault experiences decay for 1 year collateral: X * 1/e^0.1 = X * 1/1.105 and then gains X collateral • Vault collateral is now X * (1 + 1/1.105) = 1.905X • The funding rate is set to 5% per year • Position A is closed at year 2, the position experiences decay for 2 years at a rate of 5% per year, collateral: X * 1/e^0.1 = X * 1/1.105 = 0.905X • The vault experiences decay for 1 year at 5% collateral: 1.905X * 1/e^0.05 = 1.905X * 1/1.051 = 1.813X • Position A’s collateral is now removed from the vault, collateral left is 1.813X - 0.905X = 0.908 • Position B is closed at year 2, the position experiences decay for 1 year at a rate of 5%, collateral: X * 1/e^0.05 = X * 1/1.051 = 0.951X • Position B’s collateral is attempted to be removed from the vault, but the vault only has 0.908X collateral left so the position cannot be fully closed. The core issue is that every position must be updated to agree with the decay experienced by the vault, if the rate changes then every position must be updated along with the vault to decay at that time with the previous rate.

## Recommendation
Updating every position to update the rate is not feasible in an EVM environment, consider restructuring the decay to rely on a single fundingDecayAcc which accumulates for every position in the vault, similar to a rewardsPerShare model. Every position can be stamped with a last FundingDecayAcc and the decay can be measured as the difference between the latestFundingDecayAcc() - position.lastFundingDecayAcc. Then the setFundingRate function can simply update the last FundingDecayAcc using the previous rate before assigning the new rate.
