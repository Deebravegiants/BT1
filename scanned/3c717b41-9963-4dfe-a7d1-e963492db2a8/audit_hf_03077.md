# [M] Griefing attack by front-running to prevent user withdrawals.

## Summary
Severity: Medium
Contest weight: 0.1574
Dataset id: 17388
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An attacker can revert a user’s withdrawTo by front-running to deposit a dust amount of collateral in the user’s account. The collateralInvariant modifier is used to check whether the account is either empty or above the minimum collateral at the end of each withdrawTo. Meanwhile, depositTo allows deposits to an arbitrary address with no minimum deposit amount required. This opens a griefing attack vector where an attacker can frontrun any user’s withdrawTo to deposit a dust amount of collateral for the victim and make the victim's withdrawTo revert because the account is not empty after the withdrawal and the amount of remaining funds cannot meet the minimum collateral. Example scenario: 1. Alice has 1M collateral 2. Alice submits withdrawTo 1M (all the collateral) 3. Attacker frontruns Alice’s transaction to deposit 1 Wei in her account 4. Alice's withdrawal will revert with CollateralUnderLimitError The attacker can repeatedly front-run Alice's withdrawAl and effectively prevent Alice from withdrawing her collateral. This causes a denial-of-service to users’ withdrawals.

## Recommendation
Consider requiring the deposit amount to be greater than controller.minCollateral when depositTo account != msg.sender.
