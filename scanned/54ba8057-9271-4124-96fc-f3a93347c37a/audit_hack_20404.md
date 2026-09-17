# [M] 5.3.11ownershipChangecan be sidestepped

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** VotingEscrow.sol#L137-L138
**Description:** The check there is to prevent adding to managed after a transfer from or creation
require(ownershipChange[_tokenId] != block.number, "VotingEscrow: flash nft protection");

However, it doesn't prevent adding and removing from other managed tokens, merging, or splitting. For this reason,
we can sidestep the lock by splitting
BecauseownershipChangeis updated exclusively on_transferFrom, we can side-step it being set by splitting the
lock into a new one which will not have the lock.
**Recommendation:** Consider if the lock is necessary and add additional checks to prevent users from side-
stepping. Alternatively, the lock functionality may be removed to focus on maintaining underlying invariants.
**Velodrome:** Fixed in commit 02e0bc.
**Spearbit:** Verified.
