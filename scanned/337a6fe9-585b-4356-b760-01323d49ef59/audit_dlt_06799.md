# [M] MuteBond is susceptible to DOS

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-03-mute
Published: 2023-04-03
Source: https://github.com/code-423n4/2023-03-mute-findings/issues/22
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-03-mute/blob/main/contracts/bonds/MuteBond.sol#L179
https://github.com/code-423n4/2023-03-mute/blob/main/contracts/dao/dMute.sol#L75-L77
https://github.com/code-423n4/2023-03-mute/blob/main/contracts/dao/dMute.sol#L57


# Vulnerability details

## Proof of Concept
Observe that if timeToTokens is called with _lock_time = 1 week, _amount < 52, it will return 0.
https://github.com/code-423n4/2023-03-mute/blob/main/contracts/dao/dMute.sol#L57
```
function timeToTokens(uint256 _amount, uint256 _lock_time) internal pure returns (uint256){
        uint256 week_time = 1 weeks;
        uint256 max_lock = 52 weeks;

        require(_lock_time >= week_time, "dMute::Lock: INSUFFICIENT_TIME_PARAM");
        require(_lock_time <= max_lock, "dMute::Lock: INSUFFICIENT_TIME_PARAM");

        // amount * % of time locked up from min to max
        uint256 base_tokens = _amount.mul(_lock_time.mul(10**18).div(max_lock)).div(10**18);
        // apply % min max bonus
        //uint256 boosted_tokens = base_tokens.mul(lockBonus(lock_time)).div(10**18);

        return base_tokens;
    }
```

This causes lockTo to revert.
https://github.com/code-423n4/2023-03-mute/blob/main/contracts/dao/dMute.sol#L75-L77
```
 function LockTo(uint256 _amount, uint256 _lock_time, address to) public nonReentrant {
        require(IERC20(MuteToken).balanceOf(msg.sender) >= _amount, "dMute::Lock: INSUFFICIENT_BALANCE");

        //transfer tokens to this contract
        IERC20(MuteToken).transferFrom(msg.sender, address(this), _amount);

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-03-mute-findings/issues/22_
