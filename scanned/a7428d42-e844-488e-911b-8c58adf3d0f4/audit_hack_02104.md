# [M] 6.1 No Message Relayed on claim

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 3 Code Corrected

Anytime csToken.totalSupply() or funds.currentDeposit are changed, the updated values
should be transmitted to the child contract. However, the claim function does not call
sendMessageToChild. The claim function has the enforceAndUpdateBalance modifier, which in
turn calls _updateBalance. This function may modify funds.currentDeposit, and hence a
message should be relayed to the child contract.

Note that the claim function is the only function with the enforceAndUpdateBalance modifier which
does not call sendMessageToChild. Since the modifier itself can modify funds.currentDeposit, it
may make sense to include the call to sendMessageToChild in the modifier itself.


Code corrected:

A message is now relayed at the end of the claim function.
