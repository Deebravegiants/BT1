# [C] C-02 | Validate Withdraw Uses Current Total Shares

## Summary
Severity: Critical
Contest weight: 0.2504
Dataset id: 134
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _validateWithdrawalWithAction function does not use the totalShares amount saved at init in the pending action. Instead, it calculates the amount of assets a user should receive by using the current totalShares amount, together with the available balanceVault from init. Therefore reducing the totalShares amount between init and validation of a withdrawal will give the user more assets than the user should receive and vice versa. This can be exploited in the following way: • Attacker deposits funds • Attacker initiates multiple withdrawals of part of his shares for example two withdrawals of 50% of his shares • The first withdrawal is validated and reduces the totalShares amount • The second withdrawal is validated and uses the balanceVault from init but the reduced totalShares amount to calculate how many assets the attacker receives and therefore sends the attacker more assets than he should receive • Attacker repeats the process to drain the protocol All of this is independent of price changes allowing the attack to be performed swiftly and consistently.

## Recommendation
Use the totalShares amount saved at init in the pending action instead of the current one.
