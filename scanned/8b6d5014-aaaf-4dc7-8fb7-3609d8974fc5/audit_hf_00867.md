# [H] Incorrect redeemAmount Is Accounted as RA

## Summary
Severity: High
Contest weight: 0.3195
Dataset id: 2617
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When Liquidating LP , DS and CT are paired , then that amount is used to redeem RA . But the accounting for RA has been done incorrectly since it does not account for exchange rate.  
1.) Inside Liquidate LP we empty out the DS reserve and pair it up with the CT amount returned from the AMM -> ntracts/libraries/VaultLib.sol#L376  
This is the amount of CtDs being redeemed.  
2.) This same amount has been accounted for the increment in RA -> ntracts/libraries/VaultLib.sol#L390  
But this is incorrect , this is because redeemAmount is an amount in Ct/Ds not in RA , to make it into RA we need to apply the exchange rate over it(exchange rate is how many Redemption Assets you need to deposit to receive 1 Cover Token + 1 Depeg Swap and how many Redemption Assets you receive when redeeming 1 Pegged Asset + 1 Depeg Swap , read more in the Dealing with non-rebasing Pegged Assets section -> https://corkfi.notion.site/Cork-Protocol-Litepaper-f21a57d5c19d48209dfa0f0c2ab776c4).  
3.) Therefore incorrect RA amount has been accounted and incorrect amount of RA would be reserved -> ntracts/libraries/VaultLib.sol#L392  
meaning , incorrect amount of RA attributed to be withdrawn/redeemed.  
4.) This inconsistency is found at multiple places , and instead of making separate reports im listing them here ->  
contracts/libraries/PsmLib.sol#L122  
The amount here is in RA and we are issuing DS/CT with it.  
contracts/core/flash-swaps/FlashSwapRouter.sol#L368  
dsAttributed is in DS and we are depositing RA.  
contracts/libraries/VaultLib.sol#L331  
redeemAmount is in Ct/Ds here

## Recommendation
Account for the exchange rate correctly.
