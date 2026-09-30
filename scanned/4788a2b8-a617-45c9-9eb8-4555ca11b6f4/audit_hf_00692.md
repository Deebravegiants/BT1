# [M] M-13 | Only Current Mint Amount Validated

## Summary
Severity: Medium
Contest weight: 0.1253
Dataset id: 2243
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _validateMintAmount function only the current amount being minted, represented as the mintAmount is validated against the max market size and value validations. However several smaller mints could take place where each of the individual mint amounts remain below the max market validations, while the summation of the mints are above the max market validations. All of these mints may occur before a rebalance is triggered. Additionally, price action can also create an imbalance scenario that will need an increase in position size (additional size delta), which is not contemplated by _validateMintAmount. Finally, order fees could be charged incorrectly, as the outstanding size delta plus the new mint amount, could be a position decrease (i.e. minting when price moves up in a long LT).

## Recommendation
Consider validating the current outstanding rebalance sizeDelta against the market maximums as opposed to the immediate mintAmount that is currently being minted.
