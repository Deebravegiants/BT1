# [M] ActivePool does not update rewards before unwrapping wrapped asset

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-12-yetifinance
Published: 2021-12-21
Source: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/150
Type: code-finding

## Details
# Handle

kenzo


# Vulnerability details

When ActivePool sends collateral which is a wrapped asset, it first unwraps the asset, and only after that updates the rewards.
This should be done in opposite order. As a comment in WJLP's `unwrapFor` rightfully mentions - "Prior to this being called, the user whose assets we are burning should have their rewards updated".

## Impact
Lost yield for user.

## Proof of Concept
In ActivePool's `sendCollateralsUnwrap` (which is used throughout the protocol), it firsts unwraps the asset, and only afterwards calls `claimRewardFor` which will update the rewards:
[(Code ref)](https://github.com/code-423n4/2021-12-yetifinance/blob/main/packages/contracts/contracts/ActivePool.sol#L186:#L188)
```
IWAsset(_tokens[i]).unwrapFor(_to, _amounts[i]);
if (_collectRewards) {
        IWAsset(_tokens[i]).claimRewardFor(_to);
}
```
`claimRewardFor` will end up calling `_userUpdate`: [(Code ref)](https://github.com/code-423n4/2021-12-yetifinance/blob/main/packages/contracts/contracts/AssetWrappers/WJLP/WJLP.sol#L246:#L263)
```
    function _userUpdate(address _user, uint256 _amount, bool _isDeposit) private returns (uint pendingJoeSent) {
        uint256 accJoePerShare = _MasterChefJoe.poolInfo(_poolPid).accJoePerShare;
        UserInfo storage user = userInfo[_user];
        if (user.amount > 0) {
            user.unclaimedJOEReward = user.amount.mul(accJoePerShare).div(1e12).sub(user.rewardDebt);
        }
        if (_isDeposit) {
            user.amount = user.amount.add(_amount);
        } else {
            user.amount = user.amount.sub(_amount);
        }
        user.rewardDebt = user.amount.mul(accJoePerShare).div(1e12);
    }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-12-yetifinance-findings/issues/150_
