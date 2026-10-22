# [M] rescueTokens feature is broken

## Summary
Severity: Medium
Contest weight: 0.1338
Dataset id: 22982
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The rescue function is broken, and tokens cannot be rescued when needed, leading to assets being stuck in the contract.

The ClonedCoolDownHolder contains a feature that allows the protocol to recover onlyVault modifier. Thus, only the vault can call this function.

-vaults-private/contracts/vaults/staking/protocols/ClonedCoolDownHolder.sol#L2
File: ClonedCoolDownHolder.sol
22:
  /// @notice If anything ever goes wrong, allows the vault to recover lost tokens.
23:
  function rescueTokens(IERC20 token, address receiver, uint256 amount) external onlyVault {
24:
    token.checkTransfer(receiver, amount);
25:
  }
26:

However, it was found that none of the vaults could call the rescueTokens function. Thus, this feature is broken.

Medium. The rescue function is broken, and tokens cannot be rescued when needed, leading to assets being stuck in the contract.

## Recommendation
Consider allowing the protocol admin to call the rescueTokens function directly, or update the implementation of vaults to allow the vault to call the rescueTokens function.
