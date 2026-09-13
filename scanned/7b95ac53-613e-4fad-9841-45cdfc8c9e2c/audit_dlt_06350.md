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
@7:        end: vars.userLockEnd,
        caller: caller
    });
@8:    vars.newBias = newSlope.slope * (vars.userLockEnd - vars.nextPeriod);

    if(
        oldSlope.caller != caller && proxyVoterState[user][oldSlope.caller].endTimestamp > block.timestamp
    ) revert Errors.NotAllowedVoteChange();

    vars.totalPowerUsed = voteUserPower[user];
    vars.totalPowerUsed = vars.totalPowerUsed + newSlope.power - oldSlope.power;
    if(user == caller) {
        uint256 usedPower = usedFreePower[user];
        vars.oldUsedPower = oldSlope.caller != user ? 0 : oldSlope.power;
        usedPower = usedPower + newSlope.power - vars.oldUsedPower;
        if(usedPower > (MAX_BPS - blockedProxyPower[user])) revert Errors.VotingPowerExceeded();
        usedFreePower[user] = usedPower;
    } else {
        uint256 proxyPower = proxyVoterState[user][caller].usedPower;
        vars.oldUsedPower = oldSlope.caller == caller ? oldSlope.power : 0;
        proxyPower = proxyPower + newSlope.power - vars.oldUsedPower;
        if(oldSlope.caller == user) {
            usedFreePower[user] -= oldSlope.power;
        }
        if(proxyPower > proxyVoterState[user][caller].maxPower) revert Errors.VotingPowerProxyExceeded();

        proxyVoterState[user][caller].usedPower = proxyPower;
    }
    if(vars.totalPowerUsed > MAX_BPS) revert Errors.VotingPowerExceeded();
    voteUserPower[user] = vars.totalPowerUsed;

@9:    vars.oldWeightBias = _updateGaugeWeight(gauge);
@10:    vars.oldWeightSlope = pointsWeight[gauge][vars.nextPeriod].slope;

@11:    vars.oldTotalBias = _updateTotalWeight();
@12:    vars.oldTotalSlope = pointsWeightTotal[vars.nextPeriod].slope;

@13:    pointsWeight[gauge][vars.nextPeriod].bias = max(vars.oldWeightBias + vars.newBias, vars.oldBias) - vars.oldBias;
@14:    pointsWeightTotal[vars.nextPeriod].bias = max(vars.oldTotalBias + vars.newBias, vars.oldBias) - vars.oldBias;

    if(oldSlope.end > vars.nextPeriod) {
@15:        pointsWeight[gauge][vars.nextPeriod].slope = max(vars.oldWeightSlope + newSlope.slope, oldSlope.slope) - oldSlope.slope;
@16:        pointsWeightTotal[vars.nextPeriod].slope = max(vars.oldTotalSlope + newSlope.slope, oldSlope.slope) - oldSlope.slope;
    } else {
@17:        pointsWeight[gauge][vars.nextPeriod].slope += newSlope.slope;
@18:        pointsWeightTotal[vars.nextPeriod].slope += newSlope.slope;
    }

    if(oldSlope.end > block.timestamp) {
        changesWeight[gauge][oldSlope.end] -= oldSlope.slope;
        changesWeightTotal[oldSlope.end] -= oldSlope.slope;
    }
@19:    changesWeight[gauge][newSlope.end] += newSlope.slope;
@20:    changesWeightTotal[newSlope.end] += newSlope.slope;

    voteUserSlopes[user][gauge] = newSlope;
    lastUserVote[user][gauge] = block.timestamp;
}
```
`@1`: The current `period` is `Week n`.
`@2`: The next `period` is then `Week n+1`.
`@3`: Suppose user's slope is `1000`.
`@4`: Let's assume that the `lock end time` coincides exactly with the start of the next `period` i.e. `Week n+1`.
`@5`: Will be passed.
`@6`: Suppose user's power is `10%` so `slope` is `100`.
`@7`: The end time of this new `vote` will be exactly next `period` i.e. `Week n+1`.
`@8`: The `newBias` is 0, means that this new `vote` actually has `0` weight.
`@9`: Update the `gauge` weight until the next `period` i.e. `Week n+1`.
```
function _updateGaugeWeight(address gauge) internal returns(uint256) {
    uint256 ts = timeWeight[gauge];
    Point memory _point = pointsWeight[gauge][ts];
    for(uint256 i; i < 150; i++) {
        if(ts > block.timestamp) break;
        ts += WEEK;

        uint256 decreaseBias = _point.slope * WEEK;
        if(decreaseBias >= _point.bias) {
            _point.bias = 0;
            _point.slope = 0;
        } else {
            _point.bias -= decreaseBias;
            uint256 decreaseSlope = changesWeight[gauge][ts];
            _point.slope -= decreaseSlope;
        }

        pointsWeight[gauge][ts] = _point;

        if(ts > block.timestamp) {
            timeWeight[gauge] = ts;
        }
    }

    return _point.bias;
}
```
`@10`: Suppose `pointsWeight[gauge][Week n+1].slope = 2000`.
`@11`: Update the total weight until the next `period` i.e. `Week n+1`.
`@12`: Suppose `pointsWeightTotal[Week n+1].slope = 10000`,
`@13`: The `0` `newBias` doesn't affect.
`@14`: The `0` `newBias` doesn't affect.
`@15, @17`:  The `newSlope.slope` is added to `pointsWeight` for the next `period`, even though this `newSlope` will disappear in the next `period`.
Now `pointsWeight[gauge][Week n+1].slope = 2000 + 100 = 2100`.
`@16, @18`: Also is added to `pointsWeightTotal`.
`@19, @20`: These changes will not affect the future calculation of `pointWeights` because `changesWeight[gauge][Week n+1]` and `changesWeightTotal[Week n+1]` have already been applied in the previous updation in `@9`, `@11`.

So the removed `100` `slope` will permanently impact future calculations.

The reason is that we did not consider whether `newSlope.end` is greater than the start of the `nextPeriod`. 
We accounted for this condition with the `oldSlope` in lines `@15` and `@16` but missed it for the `newSlope` in lines `@17` and `@18`.
**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
Simple solution will be:
```
function _voteForGauge(address user, address gauge, uint256 userPower, address caller) internal {
-     if(vars.userLockEnd < vars.nextPeriod) revert Errors.LockExpired();
+     if(vars.userLockEnd <= vars.nextPeriod) revert Errors.LockExpired();
}
```
