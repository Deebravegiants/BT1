# [M] M-02 | Attack can game price impact at users expense

## Summary
Severity: Medium
Contest weight: 0.1889
Dataset id: 21418
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Price impact is used to incentivize bringing markets to a balanced state. However, this can be gamed by bad actors who want to profit off other users. An attacker can monitor transactions and when they see a deposit that is going to bring the market to a balanced state they can send multiple orders that do the same thing as the victim. The attacker can set the min output amount to a value greater than the input amount so that the only way the order will execute is if the order obtained the positive price impact, the rest would revert costing the user nothing more than a portion of the execution fee. After the attackers order is executed the victims order will also execute, but they will experience negative price impact since their order is moving the price away from balanced. The attacker can then withdraw, bringing the pool back to balance again. The reason this attack can be effective despite it not being certain that the attackers order will execute first is because the attacker can create many orders and only one needs to beat the victim. By sending more than one order the attacker is increasing the chance that it will be executed first and making this attack both likely to succeed and profitable in certain situations. By the end of the attack the attacker was able to obtain positive price impact twice where one of those times was at the expense of the other user.

## Recommendation
Consider refunding less of the execution fee upon cancellation to make these type of attacks unprofitable.
