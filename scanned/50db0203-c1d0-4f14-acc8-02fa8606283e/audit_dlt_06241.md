# [H] Anyone can call `batchCancelDepositAsBnftHolder` on behalf of other user

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-06
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/7
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0xa90c05833bbc1961003b8ea19c09812ee8bdcb7180080e99438c1d6872c4261d
**Severity:** high

**Description:**
**Description**\
Anyone can call `batchCancelDepositAsBnftHolder` on behalf of other user 

**Attack Scenario**\
The function `batchCancelDepositAsBnftHolder` is taking an address as an input and that address is the address of `caller` so anyone can input someone else address and `_validatorIds` and can cancel on behalf of someone else.

If you see the function `batchCancelDeposit` then instead of taking the address of `caller` it is using `msg.sender` which is a good way but taking the input is very dangerous as anyone can pu someone else addres

**Attachments**
https://github.com/GadzeFinance/dappContracts/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/StakingManager.sol#L210-L225

**Recommendation**

it is recommended to use `msg.sender` instead of taking input from user
