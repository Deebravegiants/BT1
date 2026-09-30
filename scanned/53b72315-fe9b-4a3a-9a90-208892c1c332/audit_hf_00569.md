# [C] C-02 | Insufficient Access Control On Callbacks

## Summary
Severity: Critical
Contest weight: 0.2084
Dataset id: 2031
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The afterOrderExecution function is missing a check to see if the key is one from Umami. The issue with this is that arbitrary users can currently set Umami as the callback contract and execute the logic within this callback. Part of this logic is setting the current key. If this were to change either by the attacker using a different collateral token or the opposite trading direction, the key would point to an empty position, resulting in the pps instantly decreasing by whatever the external position value is as well as making the actual external position unreachable without admin intervention. To add to this any admin intervention can then be exploited, since re-adding a position would cause a stepwise jump in pps a user could deposit prior to the action and then redeem right after to extract value from the external position.

## Recommendation
Validate that the key in the callback is from an order created by Umami.
