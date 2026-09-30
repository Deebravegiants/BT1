# [H] ISU-3 | Unbounded Call Leads To Gas Griefing and DoS

## Summary
Severity: High
Contest weight: 0.2263
Dataset id: 20602
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Issuance.completeWithdrawalEarly() is used to “buy out” a withdrawal from someone in return for the equivalent the withdrawal's value in the LST of the withdrawal or in ETH if the withdrawal was queued with wantsEth = true. That equivalent value gets sent to the oldOwner of the withdrawal either through and ERC20.transfer or through an address.call in the case of ETH. Calling an address through address.call() without a gas stipend allows the call recipient to use as much as 63/64 of the gas left for execution. This allows the recipient to do two things: 1. Maliciously expend gas in order to make the transaction be very expensive for the caller. 2. Trigger a revert, which will make the transaction fail and disallow it from being completed, thus causing DoS.

## Proof of Concept
https://github.com/GuardianAudits/RestPoCs/blob/POC_ISU-3/test/Guardian/UnboundCall.t.sol

## Recommendation
Implement the classical pull pattern, instead of the current push implementation, with regards to how the original withdrawal owner gets the payment for his withdrawal.
