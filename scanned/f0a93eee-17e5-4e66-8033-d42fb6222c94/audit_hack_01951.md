# [M] 6.8 Payable Action.execute()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The interface Executable specifies:

```
function execute(bytes calldata data, uint8[] memory paramsMap) external payable;
```
The code of actions is executed as delegatecall from within OperationExecutor.aggregate().
Delegatecall preserves msg.sender and msg.value. The aggregate function of the OperationExecutor
is not payable, hence msg.value will always be zero. Calls to executeOp() / aggregate() with
non-zero msg.value will revert, hence why is the execute function of actions supposed to be payable?

Note that actions may still work with Ether despite not receiving calls with non-zero msg.value: Ether
can be received by the DsProxies fallback function / the DsProxy can already have an Ether balance
which can be transferred onwards.

Code corrected:

OperationExecutor.executeOp() is supposed to handle Ether transactions, hence it has been
changed to payable.
