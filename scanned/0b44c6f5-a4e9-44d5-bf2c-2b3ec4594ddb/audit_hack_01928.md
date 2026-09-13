# [M] 7.3 Unable to Handle Missing Return Value

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Compared to Gearbox V1 safeApprove() has been replaced by approve() in function
CreditAccount.approveToken. The interface inherited expects a boolean return value as defined in
the ERC-20 specification. However, there are tokens such as USDT or OMG which do not adhere to this
specification and have no return value on approve() and transfer.

Calling CreditAccount.approveToken() with these tokens will revert as the function call does not
return the expected return value. Hence it's not possible for the new credit accounts to give approval on
such tokens.

Code corrected:


The new CreditAccount implementation no longer features an approveToken function. Approvals
through CreditManager.approveCreditAccount() now use the execute function of the
CreditAccount which allows arbitrary calls. This works for both, the new implementation and the old
already deployed credit accounts.

If present, the returned boolean is checked. In case the approval is unsuccessful the code attempts to
reset the approval to 0 before attempting the to approve the intended amount. This accounts for some
token implementations enforcing this.
