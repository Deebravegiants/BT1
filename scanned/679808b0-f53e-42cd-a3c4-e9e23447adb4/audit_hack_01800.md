# [M] Optimization issue

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The codebase is huge, and there are still a lot of places where these complications and gas efficiency can be improved.

#### Examples

* `_updateTopUsers`, `_updateGroupLeaders`, `_updateLeaderboard` are having a similar mechanism of adding users to a sorted set which makes more storage operations than needed:

   **code_new/contracts/LiquidityMining.sol:L473-L486**
   ```solidity
   uint256 _tmpIndex = _currentIndex - 1;
   uint256 _currentUserAmount = usersTeamInfo[msg.sender].stakedAmount;
   
   while (_currentUserAmount > usersTeamInfo[topUsers[_tmpIndex]].stakedAmount) {
       address _tmpAddr = topUsers[_tmpIndex];
       topUsers[_tmpIndex] = msg.sender;
       topUsers[_tmpIndex + 1] = _tmpAddr;
   
       if (_tmpIndex == 0) {
           break;
       }
   
       _tmpIndex--;
   }
   ```

   Instead of doing 2 operations per item that is lower than the new_item, same can be done with one operation: while `topUsers[_tmpIndex]` is lower than the new item`topUsers[_tmpIndex + 1] = topUsers[_tmpIndex]`.

* creating the Queue library looks like overkill for the intended task. It is only used for the withdrawal queue in the PolicyBook. The structure stores and processes extra data, which is unnecessary and more expensive. A larger codebase also has a higher chance of introducing a bug (and it happened here 6.

* There are a few `for` loops that are using `uint8` iterators. It's unnecessary and can be even more expensive because, under the hood, it's additionally converted to `uint256` all the time. In general, shrinking data to `uint8` makes sense to optimize storage slots, but that's not the case here.

* The value that is calculated in a loop can be obtained simpler by just having a 1-line formula:
   

   **code_new/contracts/LiquidityMining.sol:L351-L367**
   ```solidity
   function _getAvailableMonthForReward(address _userAddr) internal view returns (uint256) {
       uint256 _oneMonth = 30 days;
       uint256 _startRewardTime = getEndLMTime();
   
       uint256 _countOfRewardedMonth = countsOfRewardedMonth[usersTeamInfo[_userAddr].teamAddr][_userAddr];
       uint256 _numberOfMonthForReward;
   
       for (uint256 i = _countOfRewardedMonth; i < MAX_MONTH_TO_GET_REWARD; i++) {
           if (block.timestamp > _startRewardTime.add(_oneMonth.mul(i))) {
           _numberOfMonthForReward++;
           } else {
               break;
           }
       }
   
       return _numberOfMonthForReward;
   }
   ```

* The mapping is using 2 keys, but the first key is strictly defined by the second one, so there's no need for it:

   **code_new/contracts/LiquidityMining.sol:L60-L61**
   ```solidity
   // Referral link => Address => count of rewarded month
   mapping (address => mapping (address => uint256)) public countsOfRewardedMonth;
   ```

* There are a lot of structures in the code with duplicated and unnecessary data, for example: 


   **code_new/contracts/LiquidityMining.sol:L42-L48**
   ```solidity
   struct UserTeamInfo {
       string teamName;
       address teamAddr;
   
       uint256 stakedAmount;
       bool isNFTDistributed;
   }
   ```
    
   Here the structure is created for every team member, duplicating the team name for each member.

#### Recommendation

Optimize and simplify the code.
