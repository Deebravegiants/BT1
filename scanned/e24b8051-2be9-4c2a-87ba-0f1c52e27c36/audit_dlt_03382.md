# [M] Unchecked return value of `transferFrom` in function `timeLockERC20`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-visorfinance
Published: 2021-05-20
Source: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/69
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

In the function `timeLockERC20` (line 610), the return value of `IERC20.transferFrom` is unchecked. The return value could be `false` if the transferred token is not ERC20-compliant, indicating that the transfer fails. In that case, the variable `timelockERC20Balances` will be inconsistent with the vault's actual balance.

## Proof of Concept

Referenced code:
[Visor.sol#L610](https://github.com/code-423n4/2021-05-visorfinance/blob/main/contracts/contracts/visor/Visor.sol#L610)

## Tools Used

None

## Recommended Mitigation Steps

Use `TransferHelper.safeTransfer` instead as in the function `timeUnlockERC20` (at line 637).
