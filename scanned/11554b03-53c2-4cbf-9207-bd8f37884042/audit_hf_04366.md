# [H] H-04 | Dust Amount DoS

## Summary
Severity: High
Contest weight: 0.2369
Dataset id: 21571
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the OFT token receives a request to send amountLD of tokens, it will deduct some dust amount from that. After that a slippage check is performed and if amountLD - dustAmount is less than a given minAmountLD, the transaction will revert. The problem found in OCCManager and LedgerOCCManager is that both amountLD and dustAmount are set to the same value. This will result in inability to transfer tokens when there is a dust amount present, meaning no staking, withdrawing, claiming can be performed with these amounts. Ignoring the UX issues, this can be quite problematic for unstaking and vesting esOrder. Imagine that a user has some esAmount that they unstake and vest. After the vesting period ends, the user is not able to claim their order tokens because esAmount has dust amount to be removed.

## Recommendation
A possible solution may be to pass the cleared amountLD as minAmountLD. However, this can lead to some minor token losses when sending a message from the Ledger side to the Vault side. If you want to mitigate these, you can add an additional state variable that tracks dust amounts and adds them to the respective users' balances.
