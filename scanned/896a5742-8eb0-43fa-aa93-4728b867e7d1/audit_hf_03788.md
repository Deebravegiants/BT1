# [M] Fee on transfer tokens will break the with-

## Summary
Severity: Medium
Contest weight: 0.1700
Dataset id: 19996
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a currency has a built-in transfer fee, withdrawing prime cash may be impossible due to accounting discrepancies. Example: Alice has 100 pUSDT, equivalent to 105 USDT, and assume that all the underlying USDT is in Compound V3 (in form of cUSDT), earning interest. When Alice withdraws the prime cash using the withdraw() function in AccountsAction.sol, the function checks if the corresponding underlying (105 USDT) is available in the contract. Since all the USDT is lent out in Compound, Notional initiates the redemption process. The redemption process attempts to withdraw 105 USDT worth of cUSDT from Compound. However, due to transfer fees on USDT, redeeming 105 USDT worth of cUSDT results in approximately 104.9 USDT. The require check ensures that Notional must withdraw 105 USDT or more, but in reality, only 104.9 USDT is withdrawn, causing the function to revert consistently. Since this is an unlikely scenario I'll label it as medium. However, if fee on transfer tokens will be used this can be a high finding since withdrawals will not go through at all. USDT can open it's transfer functionality so that should be also taken into consideration if such thing happens.

## Recommendation
Instead of promising the underlying amount on withdrawals, just return the withdrawn pcashs corresponding yield tokens underlying amount and let users endorse the loss
