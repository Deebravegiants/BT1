# [M] Delegated transfer of owner fails

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-19
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/119
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details


## Vulnerability Details

The `Visor.delegatedTransferERC20` function skips the approval check if `msg.sender == _getOwner()`, however, it will still try to reduce the approval in that case.
As it is implemented that the owner does not need an approval for this function, a previous approve action was most likely never sent and the transaction will fail when trying to reduce the `erc20Approvals` field by the `amount` due to the usage of SafeMath underflow checks.

## Impact

Owners cannot transfer using this function.

## Recommended Mitigation Steps

Move the approval subtraction to the `if` path.
