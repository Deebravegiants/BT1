# [M] 6.1 Missing ETH Unwrapping

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The AutomationExecutor allows its owner to withdraw tokens or native ETH. As the Oazo team
informed us, the main purpose of this function is to withdraw ETH converted from DAI. The exchange
contract is not able to handle native ETH but needs its wrapped version. Hence there is a need for
unwrapping functionality to be able to use native ETH. However, such functionality is not implemented.

Code corrected:

unwrapWETH has been implemented. It can be called only by the owner of the AutomationExecutor
contract and calls weth.withdraw function.
