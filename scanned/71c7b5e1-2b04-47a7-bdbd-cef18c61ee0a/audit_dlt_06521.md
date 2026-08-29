# [M] OOG on `claimRemovedTokens` loop due to potential large gap between `lastClaimedUserId` and `_currentSnapshotId`

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-25
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/75
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x71f125e47e58aa7ba73cdde503cb3c4f9a44f7aef33c969e60ff1408b5dfe388
**Severity:** medium

**Description:**
**Description:**

In an edge case scenario, where a user is a passive one, maybe because of deposit, claim and withdrew while ago, or they rarely `claimRemovedTokens`, there is a potential large gap between `lastClaimedUserId` and `_currentSnapshotId`. For example, if `lastClaimedUserId` is 10, and `_currentSnapshotId` is 300, is a possible condition.

Snapshot ID is incremental and used for versioning of token updates. Everytime there is a token removal in Rebalancing contract, this snapshot will be incremented.

Current code in `claimRemovedTokens` use `hasInteractedWithId` to flag if user should be interact with the removed token, means, if the `hasInteractedWithId` is `true` then `claimRemovedTokens` will assign `_balanceOfLastValidId` and try to `attemptClaim`.

This `hasInteractedWithId` can be gamed by a 1 wei donation of portfolio token to a user.
By transfering 1 wei of portfolio token to a passive user, (this will trigger `PortfolioToken::_afterTokenTransfer` -> `UserManagement::_updateUserRecord` -> `TokenExclusionManager::_setUserRecord`) it will then set the `hasInteractedWithId` to `true`, then `attemptClaim` will always be executed, passed the `_portfolioTokenBalance > 0` check, then it will try to transfer the removed token, even if it's 1 wei balance, which then rounded to 0. 

Having this situation, with large gap between snapshot id, and each loop there is a transfer token, there is a potential Out of Gas issue here.

```js
File: TokenExclusionManager.sol
125:   function claimRemovedTokens(address user) external override nonReentrant {
127:     // Retrieve the current snapshot ID for processing
128:     uint256 _currentId = _currentSnapshotId;
...
132:     // Fetch the last snapshot ID for which the user claimed removed tokens
133:     uint256 lastClaimedUserId = lastClaimedRemovedTokenId[user];
134: 
135:     // Initialize variable to keep track of the user's balance at the last valid snapshot ID
136:     uint256 _balanceOfLastValidId;
137: 
138:     // Iterate over snapshot IDs from the last claimed to the current ID
139: @>  for (uint256 id = lastClaimedUserId + 1; id < _currentId; id++) {
...
145:       // Fetch user data for the current snapshot ID
146:       UserRecordData memory userData = userRecord[user][id];
147: 
148:       // Update _balanceOfLastValidId with current snapshot balance and clean up user record if user interacted with this ID
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/75_
