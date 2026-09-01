# [H] Attacker Can Frontruns User's Withdrawals To Make Them Reverts Without Costs

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-dyad
Published: 2024-04-25
Source: https://github.com/code-423n4/2024-04-dyad-findings/issues/930
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L127


# Vulnerability details

## Impact

User's withdrawals will be prevented from success and an attacker can keep up without a cost using fake vault and fake token.

## Proof of Concept

There is a mechanisms for a flash loan protection that saves the current block number in a mapping of dNft token id, and then prevent it from withdrawing at the same block number, as we can see in the `VaultManagerV2::deposit()` function which can be called by anyone with a valid dNft id:

```solidity
src/core/VaultManagerV2.sol:
  119:   function deposit(
  120:     uint    id,
  121:     address vault,
  122:     uint    amount
  123:   ) 
  124:     external 
  125:       isValidDNft(id)
  126:   {
@>127:     idToBlockOfLastDeposit[id] = block.number;
  128:     Vault _vault = Vault(vault);
  129:     _vault.asset().safeTransferFrom(msg.sender, address(vault), amount);
  130:     _vault.deposit(id, amount);
  131:   }
```

The attacker can use this to prevent any withdrawals in the current block, since it will be checked whenever an owner of dNft token try to withdraw:

```solidity
src/core/VaultManagerV2.sol:
  134:   function withdraw(
  135:     uint    id,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-dyad-findings/issues/930_
