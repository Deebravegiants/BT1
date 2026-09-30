# [M] Anyone can avoid receiving bad debt dis-

## Summary
Severity: Medium
Contest weight: 0.2143
Dataset id: 2634
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol implements redistribution of a liquidated Den's bad debt during its liquidation. This bad debt will be shared to the remaining dens of the Den Manager. However, any user can prevent receiving bad debt if they will close their dens right before liquidation. This could result race condition and every one want to close their dens. If there is only 1 den remained open, he will receive all bad debts which will further increase his debt. This can have a devastating impact because either he will be forced to pay that debt to recover the collateral or be liquidated. There is no preventive measure applied by the protocol in this kind of situation. The current protocol design somehow allows it to happen. Closing of den can be freely executed anytime the user want in which can't be help during this kind of situation. Internal Pre-conditions 1. Den with large bad debt is being liquidated. External Pre-conditions Attack Path This can be the scenario. 1. There are 3 remaining dens in the den manager. Den A, B and C. 2. Den A and B each hold the same amount of collateral and debt and in healthy state while C is in near liquidation risk. 3. Suddenly, collateral price drops and Den C accumulated bad debt. 4. Den B owner knew about vulnerability and immediately closed his den right before liquidation. 5. At this point, only 1 den remaining which is Den A, in which it receives all bad debt distribution from Den C liquidation. This can impact the remaining Dens that will unfairly receive the bad debt. This will increase their debt and forced to pay for it to recover their collateral or avoid liquidation.

## Recommendation
Apply a mechanism in which there is a time delay of closing den during imminent liquidation of bad debt. Making sure the debt distribution is fair for everyone.
