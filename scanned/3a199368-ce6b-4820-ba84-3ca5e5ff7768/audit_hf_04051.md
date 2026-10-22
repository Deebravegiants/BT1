# [H] isCoolerCallback can be bypassed

## Summary
Severity: High
Contest weight: 0.3598
Dataset id: 20490
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The CoolerCallback.isCoolerCallback() is intended to ensure that the lender implements the CoolerCallback abstract at line 241 when the parameter isCallback_ is true. #L233-L275 However, this function doesn't provide any protection. The lender can bypass this check without implementing the CoolerCallback abstract by calling the Cooler.clearRequest() function using a contract that implements the isCoolerCallback() function and returns a true value. For example: By being the loan.lender with implement only onDefault() function, this will cause the repayLoan() and rollLoan() methods to fail due to revert at onRepay() and onRoll() function. The borrower cannot repay and the loan will be defaulted. After the loan default, the attacker can execute claimDefault() to claim the collateral. Furthermore, there is another method that allows lenders to bypass the CoolerCallback.isCoolerCallback() function which is loan ownership transfer. Normally, the lender who implements the CoolerCallback abstract may call the Cooler.clearRequest() with the _isCoolerCallback parameter set to true to execute logic when a loan is repaid, rolled, or defaulted. But the lender needs to change the owner of the loan, so they call the approveTransfer() and transferOwnership() functions to the contract that doesn't implement the CoolerCallback abstract (or implement only onDefault() function to force the loan default), but the loan.callback flag is still set to true. Thus, this breaks the business logic since the three callback functions don't need /// @notice Allows for debt issuers to execute logic when a loan is repaid, rolled, or defaulted. /// @dev The three callback functions must be 1. The lender forced the Loan become default to get the collateral token, owner lost the collateral token. 2. Bypass the isCoolerCallback validation.

## Recommendation
Only allowing callbacks from the protocol-trusted address (eg., Clearinghouse contract). Disable the transfer owner of the loan when the loan.callback is set to true.
