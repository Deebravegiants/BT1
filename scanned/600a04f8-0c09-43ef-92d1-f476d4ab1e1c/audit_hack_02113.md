# [M] 6.2 ERC20 Token Decimals

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The GatewayToken contract inherits from ERC20Upgradeable fixed decimals of 18. In general, this
might be not the same as the original token decimals. As a result, this might break UIs that will deal with
such bridged tokens. Also, protocols that rely on decimals might have problems with compatibility.


Code corrected:

The GatewayToken.decimals now returns a variable that can be set in the init function.
