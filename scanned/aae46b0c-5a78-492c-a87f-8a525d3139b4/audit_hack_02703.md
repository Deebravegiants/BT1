# [M] Queue.sol ERC20 missing return value check

## Summary
Severity: Medium
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L204
Type: audit-issue

## Details
# Queue.sol ERC20 missing return value check

## Summary
The processDeposits() function performs an ERC20.approve() call but does not check the success return value.
Some tokens do not revert if the approval failed but return false instead.

## Vulnerability Detail

## Impact
Tokens that don't actually perform the approve and return false are still counted as a correct approve.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L204

     'ERC20.approve(address(Vault), deposits);'

## Tool used

Manual Review

## Recommendation
We recommend using [OpenZeppelin’s SafeERC20](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v4.1/contracts/token/ERC20/utils/SafeERC20.sol#L74) versions with the safeApprove function that handles the return value check as well as non-standard-compliant tokens.
