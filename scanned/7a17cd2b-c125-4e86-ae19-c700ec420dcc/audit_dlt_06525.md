# [M] Users Unable to Claim Removed Tokens Due to Transfer Failures in claimRemovedTokens Function

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-22
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/60
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x2a60e4e670f79bb68f964cd50c776c60f0a87c58f61272a1ec41950ee8dbcd2e
**Severity:** medium

**Description:**
**Description**\
The `claimRemovedTokens` function is designed to allow users to claim their share of tokens that have been removed in previous snapshots. The function iterates over all snapshot IDs from the last claimed ID to the current snapshot ID, attempting to claim the user's share of each removed token using the `attemptClaim` function. The `safeTransfer` function within `attemptClaim` is used to transfer the calculated share to the user. If the transfer fails for any reason, the entire `claimRemovedTokens` function reverts, preventing the user from claiming any of their removed tokens.

Here is the relevant portion of the code for the `claimRemovedTokens` function:

```solidity
function claimRemovedTokens(address user) external override nonReentrant {
    if (user == address(0)) revert ErrorLibrary.InvalidAddress();
    uint256 _currentId = _currentSnapshotId;
    if (_currentId < 2) revert ErrorLibrary.NoTokensRemoved();
    uint256 lastClaimedUserId = lastClaimedRemovedTokenId[user];
    uint256 _balanceOfLastValidId;

    for (uint256 id = lastClaimedUserId + 1; id < _currentId; id++) {
        uint256 totalSupply = totalSupplyRecord[id];
        address currentRemovedToken = removedToken[id].token;
        uint256 tokenBalanceAtRemoval = removedToken[id].balanceAtRemoval;
        UserRecordData memory userData = userRecord[user][id];

        if (userData.hasInteractedWithId) {
            _balanceOfLastValidId = userData.portfolioBalance;
            delete userRecord[user][id];
        }

        attemptClaim(currentRemovedToken, user, _balanceOfLastValidId, tokenBalanceAtRemoval, totalSupply);
    }

    if (!userRecord[user][_currentId].hasInteractedWithId) {
        _setUserRecord(user, _balanceOfLastValidId);
    }

    _setLastClaimedId(user, _currentId - 1);
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/60_
