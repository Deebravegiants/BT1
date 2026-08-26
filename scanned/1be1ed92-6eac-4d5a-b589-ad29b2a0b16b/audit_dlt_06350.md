# [M] Removed user's slope will impact the calculation of future points.

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-16
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/62
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xe1c4f15967fb727d49dac42c2e4e7e75974c0fd5fa5fe2d51874a80493ad0018
**Severity:** medium

**Description:**
**Description**\
When a user `votes` on the `gauge`, the previous `vote` is replaced by the new one. 
However, if the user's `lock end time` coincides exactly with the start of the next `period`, there may be an incorrect update.

**Attack Scenario**\
The following function is called when a user `votes` on a `gauge`.
```
function _voteForGauge(address user, address gauge, uint256 userPower, address caller) internal {
    VoteVars memory vars;

@1:    vars.currentPeriod = (block.timestamp) / WEEK * WEEK;
@2:    vars.nextPeriod = vars.currentPeriod + WEEK;
@3:    vars.userSlope = IHolyPalPower(hPalPower).getUserPointAt(user, vars.currentPeriod).slope;
@4:    vars.userLockEnd = IHolyPalPower(hPalPower).locked__end(user);

    if(!_isGaugeListed(gauge)) revert Errors.NotListed();

@5:    if(vars.userLockEnd < vars.nextPeriod) revert Errors.LockExpired();
    
    if(userPower > MAX_BPS) revert Errors.VotingPowerInvalid();
    if(block.timestamp < lastUserVote[user][gauge] + VOTE_COOLDOWN) revert Errors.VotingCooldown();

    _clearExpiredProxies(user);

    VotedSlope memory oldSlope = voteUserSlopes[user][gauge];
    if(oldSlope.end > vars.nextPeriod) {
        vars.oldBias = oldSlope.slope * (oldSlope.end - vars.nextPeriod);
    }

    VotedSlope memory newSlope = VotedSlope({
@6:        slope: (convertInt128ToUint128(vars.userSlope) * userPower) / MAX_BPS,
        power: userPower,
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/62_
