# [H] 6.16 Setting Wrong State Variable

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The function _setOperatorParams in VaultGovernance, as the name suggests, should update the
state variable _operatorParams, instead it overwrites the variable _protocolParams:

```
function _setOperatorParams(bytes memory params) internal {
_requireAtLeastOperator();
_protocolParams = params;
}
```
This mistake has severe consequences: operator gets admin privileges to set _protocolParams or can
set a vault state to incorrect parameters. Finally, the functionality to initialize or update the
_operatorParams is missing.

Code corrected:

The issue is resolved and now the function _setOperatorParams sets the operator params as
intended. The natspec description has been updated accordingly also.
