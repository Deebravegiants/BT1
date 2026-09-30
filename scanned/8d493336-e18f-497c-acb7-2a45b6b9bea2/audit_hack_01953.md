# [M] 6.10 Visibility of aggregate Function

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Although the main entry point into the OperationExecutor contract is the executeOp function, the
aggregate function is also public. In the current implementation this is required for the flashloan
functionality to continue execution of the subsequent calls.

This function, which is not intended to be called directly, may become a source of confusion/errors. In
particular, if called directly it will bypass the verification that the right actions are executed for a given
operation (as specified by OperationsRegistry). Furthermore operationStorage.finalize()
will not be executed.

Access to this function might be restricted. This function may be internal, with an exposed external
function for onFlashloan() which accepts calls by the OperationExecutor only.

Code corrected:

The visibility of the aggregate function has been changed to internal. The callback from
onFlashLoan to the DsProxy is executed via a new callbackAggregate function which is public but
restricts execution only by OperationExecutor itself.
