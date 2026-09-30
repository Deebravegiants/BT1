# [M] function timeLockERC20 does not check the return value of transferFrom

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-visorfinance
Published: 2021-05-17
Source: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/5
Type: code-finding

## Details
# Handle

paulius.eth


# Vulnerability details

## Impact
function timeLockERC20 uses transferFrom for erc20 transfers, however, it does not check the return value. According to the ERC20 standard, this function should return a boolean to indicate success. Not checking that may not work with some tokens that, for example, return false if the transfer fails. 

## Recommended Mitigation Steps
I see 2 mitigation options:
1) Use safeTransferFrom
2) check balanceOf before and after and ensure that balanceAfter >= balanceBefore.add(amount).
