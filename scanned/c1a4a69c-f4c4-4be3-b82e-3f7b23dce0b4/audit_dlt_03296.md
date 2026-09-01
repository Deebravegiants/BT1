# [M] Reward not transferred correctly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-12-yetifinance
Published: 2021-12-21
Source: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/137
Type: code-finding

## Details
# Handle

csanuragjain


# Vulnerability details

## Impact
Monetary loss for user

## Proof of Concept
1. Navigate to contract at https://github.com/code-423n4/2021-12-yetifinance/blob/main/packages/contracts/contracts/AssetWrappers/WJLP/WJLP.sol

2. Let us see _sendJoeReward function

```
function _sendJoeReward(address _rewardOwner, address _to) internal {
        // harvests all JOE that the WJLP contract is owed
        _MasterChefJoe.withdraw(_poolPid, 0);

        // updates user.unclaimedJOEReward with latest data from TJ
        _userUpdate(_rewardOwner, 0, true);

        uint joeToSend = userInfo[_rewardOwner].unclaimedJOEReward;
        userInfo[_rewardOwner].unclaimedJOEReward = 0;
        _safeJoeTransfer(_to, joeToSend);
    }
```

3. Lets say user reward are calculated to be 100 so _safeJoeTransfer is called with joeToSend as 100. Also user remaining reward becomes 0

4. Let us see _safeJoeTransfer function

```
function _safeJoeTransfer(address _to, uint256 _amount) internal {
        uint256 joeBal = JOE.balanceOf(address(this));
        if (_amount > joeBal) {
            JOE.transfer(_to, joeBal);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/137_
