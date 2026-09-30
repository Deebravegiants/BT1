# [H] VAULT-1 | Withdrawal Cooldown Can Be Bypassed

## Summary
Severity: High
Contest weight: 0.2880
Dataset id: 20575
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In ParifiVault, the cooldown function only checks that the balance of a sender is not 0. It does not check how many tokens the user has or the amount that could be withdrawn after the cooldown period. A user may:
Prepare X addresses for which it sends 1 WEI of share tokens
Call the ParifiVault.cooldown function from each address
Rotate this system in order to also bypass the expiry window constraint
Whenever a user wishes to withdraw any amount of LPs, they send all token shares to one of the pre-warmed addresses and withdraw reserves
Because the cooldown can be avoided, a depositor can view a profitable position but withdraw their liquidity without waiting. This is extremely detrimental to traders as they will be unable to withdraw their profits due to the lack of reserves.
Due to the bypassed cooldown, profit from the vault may also be extracted with the following steps:
Flash-loan a large amount of tokens
Deposit the tokens into the vault
Create a new position that triggers [fee distribution](https://github.com/GuardianAudits/PariFi-10-2023/blob/main/src/OrderManager.sol#L684-L687) and increases the value per share
Withdraw tokens using a pre-warmed address and profit

## Recommendation
Note the balance of users that call the cooldown function and allow a maximum of that amount to be withdrawn in redeem and withdraw functions. Alternatively, reset the cooldown on shares transfer and deposit.
