# [M] VaultBase.sol is not EIP4626 compliant

## Summary
Severity: Medium
Reporter: 0x52
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultBase.sol#L13-L106
Type: audit-issue

## Details
# VaultBase.sol is not EIP4626 compliant

## Summary

VaultBase.sol is not EIP4626 compliant which can cause issue for both this project and any project that integrates with it due to unexpected behavior from what are expected to be EIP4626 compliant methods.

## Vulnerability Detail

[EIP-4626](https://eips.ethereum.org/EIPS/eip-4626) specifies certain requirements for methods to be compliant. The following functions don't meet these requirements:

maxRedeem/maxWithdraw are required to return 0 when redeems/withdraws are paused. This occurs when the auction is ongoing. Since the base methods have not been overridden they will return the wrong values when they are paused.

maxDeposit/maxMint are required to return 0 when they are not available. Since they are limited to only the queue, they should return 0 to everyone but the queue contract 

## Impact

Noncompliance can cause issues for both the project and any other project that integrates them

## Code Snippet

[VaultBase.sol#L13-L106](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultBase.sol#L13-L106)

## Tool used

Manual Review

## Recommendation

The functions discussed above should be added to VaultBase.sol as overrides to ensure compliance with EIP-4626
