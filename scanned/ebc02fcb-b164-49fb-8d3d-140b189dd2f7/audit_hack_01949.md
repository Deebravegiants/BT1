# [M] 6.6 No Access Control on onFlashLoan

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The onFlashLoan function of the OperationExecutor contract is only intended to be called by the
Flashloan provider. As it has no access control it can be called by anyone. The contract will then give
approval to the registered lender for amount of asset. While this is not necessarily a problem, it breaks
the normal pattern that the OperationExecutor is "stateless" in between calls, in the sense that he has
given an approval to transfer tokens to a third party.

Code corrected:

Access control has been added to OperationExecutor.onFlashLoan(). The function can only be
called by the trusted lender returned by the Registry:

```
address lender = registry.getRegisteredService(FLASH_MINT_MODULE);
require(msg.sender == lender, "Untrusted flashloan lender");
```
