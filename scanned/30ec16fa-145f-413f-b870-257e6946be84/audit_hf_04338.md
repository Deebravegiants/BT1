# [M] M-13 | Attackers Can Borrow With Zero Interest

## Summary
Severity: Medium
Contest weight: 0.2033
Dataset id: 21494
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can borrow reserve tokens by adding bAssets as collateral to the system and interests for these credits are paid upfront based on a daily rate and the baseline value. Credits are created based on the baseline value of the bAssets, and interests are also paid based on the baseline value when the credit is created. However, this baseline value only increases in time, which means that more reserves can be borrowed with the same collateral when the baseline value increases. And lastly, the protocol [has a check](https://github.com/GuardianAudits/baseline-team-2-pocs/blob/7aa793fec8884f284f09c2995b8da3bbe97a9a0a/src/policies/CreditFacility.sol#L125C1-L126C76) to ensure the borrow is legitimate (either extension of existing borrow or new borrow). But, this check is incorrect and a user can still borrow without extending and without increasing the collateral. Attackers can combine all of these to borrow zero interest credits: 1. Attacker buys bAssets or already holds. 2. Creates a very long term credit when the blv is as low as possible. The interest is paid at this step. 3. Waits for blv to increase. 4. Borrows again without increasing the collateral and without extending expiry. 5. This second borrow will transfer more reserves due to increased blv, but the interest will be 0. 6. Attacker can do it repetitively every time the blv increases. The attacker basically setup his future credits, and paid the interest for them at a very low price, making them effectively free.

## Recommendation
Do not allow credits that are not legitimate. Also, charge interest based on the total extra credit instead of charging based on newly added collateral to prevent lost interest in case of blv increase.
