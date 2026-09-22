# [M] 5.2.15 Check__GAPs

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** LPToken.sol#L16, OwnerPausableUpgradeable.sol#L16, StableSwap.sol#L39, Merkle.sol#L37,
ProposedOwnable.sol#L193
**Description:** All__GAPs have the same size, while the different contracts have a different number of storage
variables. If the__GAPsize isn't logical it is more difficult to maintain the code.
Note: set to a risk rating of medium because the probably of something going wrong with future upgrades is low to
medium, and the impact of mistakes would be medium to high.
LPToken.sol: uint256[49] private __GAP;// should probably be 50
OwnerPausableUpgradeable.sol: uint256[49] private __GAP;// should probably be 50
StableSwap.sol: uint256[49] private __GAP;// should probably be 48
Merkle.sol: uint256[49] private __GAP;// should probably be 48
ProposedOwnable.sol: uint256[49] private __GAP;// should probably be 47


**Recommendation:** Check and update the__GAPs of all the contracts. Perhaps the__GAPofProposedOwnable-
Upgradeableshould be moved toProposedOwnable.
**Connext:** Solved in PR 2342.
**Spearbit:** Verified.
