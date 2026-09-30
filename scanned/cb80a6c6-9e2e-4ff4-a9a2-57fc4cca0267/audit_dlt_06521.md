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
149:       if (userData.hasInteractedWithId) {
150: @>      _balanceOfLastValidId = userData.portfolioBalance;
151:         delete userRecord[user][id];
152:       }
153: 
154:       // Attempt to claim the user's share of the removed token based on their portfolio balance (if > 0) at the last valid snapshot
155:       attemptClaim(
156:         currentRemovedToken,
157:         user,
158: @>      _balanceOfLastValidId,     // @audit : 1 wei 
159:         tokenBalanceAtRemoval,
160:         totalSupply
161:       );
162:     }
...
185:   function attemptClaim(
186:     address _removedToken,
187:     address _user,
188:     uint256 _portfolioTokenBalance,
189:     uint256 _balanceAtRemoval,
190:     uint256 _totalSupply
191:   ) private {
192: @>  if (_portfolioTokenBalance > 0) {  // @audit : 1 wei can skip this check
193:       // Calculate the user's share of the removed token
194:       uint256 balance = (_balanceAtRemoval * _portfolioTokenBalance) /
195:         _totalSupply;
196:       // Transfer the calculated share to the user
197:       TransferHelper.safeTransfer(_removedToken, _user, balance); // @audit : even if balance 0, can still transfer, consume gas
198:     }
199:   }
...
219:   function _setUserRecord(address _user, uint256 _userBalance) internal {
220:     userRecord[_user][_currentSnapshotId].portfolioBalance = _userBalance;
221:     userRecord[_user][_currentSnapshotId].hasInteractedWithId = true;
222:   }

File: PortfolioToken.sol
139:   function _afterTokenTransfer(
140:     address _from,
141:     address _to,
142:     uint256 _amount
143:   ) internal override {
144:     super._afterTokenTransfer(_from, _to, _amount);
145:     if (_from == address(0)) {
146:       _updateUserRecord(_to, balanceOf(_to));
147:     } else if (_to == address(0)) {
148:       _updateUserRecord(_from, balanceOf(_from));
149:     } else {
150:       _updateUserRecord(_from, balanceOf(_from));
151:       _updateUserRecord(_to, balanceOf(_to));
152:     }
153:   }
```

**Scenario:**

1. Alice is a passive user who previously deposited, claimed removed tokens, and withdrew her assets, leaving her `lastClaimedRemovedTokenId` for example at 7.
2. After Alice withdrew all her assets, Bob transfers 1 wei of the portfolio token to Alice's address when the current snapshot ID was 10.
3. Several months later, the portfolio's current snapshot ID is 300, and Alice decides to deposit again.
4. When Alice calls `claimRemovedTokens`:
   - The loop starts from ID 8 and goes up to ID 300.
   - Since `hasInteractedWithId` was set to true at ID 10, it will attempt to `attemptClaim` at each iteration, even if the transfer balance is 0.
5. This extensive looping and repeated claim attempts could lead to an out-of-gas error, preventing Alice from completing her claim.

**Impact:**

The potential for an out-of-gas error due to a potential large gap between `lastClaimedUserId` and `_currentSnapshotId` can prevent users from successfully claiming removed tokens, especially if there are many snapshots to process.

**Mitigation:**

Consider implementing mechanisms such as limiting the number of iterations per transaction, allowing users to batch their claims over multiple transactions
