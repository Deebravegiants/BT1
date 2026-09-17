# [M] 6.1 IERC20 Incompatible With Tether

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

USDT, one of the collaterals, is not fully ERC20 compliant, notably some features lack the mandatory
return value to comply with the standard.

In MultiplyProxyActions the interface IERC20 is used to interact with the token contracts. In the
interface definition a return value is expected for e.g., the approve and the transfer functions. Hence
the Solidity compiler generates bytecode that expects a return value and reverts if there is none.

Risk accepted:

Oazo Apps Limited replied:


```
Currently, Tether is not used as collateral in Maker Protocol.
In case Tether is onboarded to Maker Protocol,
the multiply feature will be disabled for it.
```
