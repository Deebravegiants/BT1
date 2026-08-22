# [M] `rescueTokens` feature is broken

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-06-leveraged-vaults
Published: 2024-07-03
Source: https://github.com/sherlock-audit/2024-06-leveraged-vaults-judging/issues/72
Type: sherlock-finding

## Details
xiaoming90

Medium

# `rescueTokens` feature is broken

## Summary

The rescue function is broken, and tokens cannot be rescued when needed, leading to assets being stuck in the contract.

## Vulnerability Detail

The `ClonedCoolDownHolder` contains a feature that allows the protocol to recover lost tokens, as per the comment in Line 22 below. This function is guarded by the `onlyVault` modifier. Thus, only the vault can call this function.

https://github.com/sherlock-audit/2024-06-leveraged-vaults/blob/main/leveraged-vaults-private/contracts/vaults/staking/protocols/ClonedCoolDownHolder.sol#L23

```solidity
File: ClonedCoolDownHolder.sol
22:     /// @notice If anything ever goes wrong, allows the vault to recover lost tokens.
23:     function rescueTokens(IERC20 token, address receiver, uint256 amount) external onlyVault {
24:        token.checkTransfer(receiver, amount);
25:     }
26: 
```

However, it was found that none of the vaults could call the `rescueTokens` function. Thus, this feature is broken.

## Impact

Medium. The rescue function is broken, and tokens cannot be rescued when needed, leading to assets being stuck in the contract.

## Code Snippet

https://github.com/sherlock-audit/2024-06-leveraged-vaults/blob/main/leveraged-vaults-private/contracts/vaults/staking/protocols/ClonedCoolDownHolder.sol#L23

## Tool used

Manual Review

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2024-06-leveraged-vaults-judging/issues/72_
