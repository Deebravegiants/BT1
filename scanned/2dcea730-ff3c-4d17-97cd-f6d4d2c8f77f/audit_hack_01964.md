# [H] 6.11 Incorrect Parameters on externalCall

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The function signOrder in LStrategy performs few externalCall s, and for one of them sets the
wrong parameters as input:

```
bytes memory setPresignatureData = abi.encode(SET_PRESIGNATURE_SELECTOR, uuid, signed);
erc20Vault.externalCall(cowswap, SET_PRESIGNATURE_SELECTOR, setPresignatureData);
```
Note that the function selector is part of the abi.encode and then is set as the second parameter in
externalCall, which also appends the selector when executing the call, hence causing the external
function to always fail:

```
(bool res, bytes memory returndata) = to.call{value: msg.value}(abi.encodePacked(selector, data));
```
Code corrected:

The external call in LStrategy.signOrder does not encode the SET_PRESIGNATURE_SELECTOR
twice anymore.
