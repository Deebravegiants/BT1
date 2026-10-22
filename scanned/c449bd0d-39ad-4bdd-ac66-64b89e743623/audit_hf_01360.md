# [M] Check __GAPs

## Summary
Severity: Medium
Contest weight: 0.3933
Dataset id: 6852
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All __GAPs have the same size, while the different contracts have a different number of storage variables. If the __GAP size isn't logical it is more difficult to maintain the code.
Note: set to a risk rating of medium because the probably of something going wrong with future upgrades is low to medium, and the impact of mistakes would be medium to high.

```solidity
LPToken.sol:
uint256[49] private __GAP; // should probably be 50

OwnerPausableUpgradeable.sol: uint256[49] private __GAP; // should probably be 50

StableSwap.sol:
uint256[49] private __GAP; // should probably be 48

Merkle.sol:
uint256[49] private __GAP; // should probably be 48

ProposedOwnable.sol:
uint256[49] private __GAP; // should probably be 47
```

## Recommendation
Check and update the __GAPs of all the contracts. Perhaps the __GAP of ProposedOwnableUpgradeable should be moved to ProposedOwnable.
