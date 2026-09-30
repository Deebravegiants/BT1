# [M] Proper Claim of Fee in claimableTokens()

## Summary
Severity: Medium
Contest weight: 0.4610
Dataset id: 12281
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LightDAO governance protocol, the admin fees withdrawn from the SwapPair are transferred to the GaugeFeeDistributor and the FeeDistributor in the format of HOPE. The HOPE can be claimed by the community for their holding of veLT and the voting for the gauges. While examining the claiming of the HOPE rewards via the GaugeFeeDistributor::claimableTokens() routine, we notice it updates user's claim state but does not transfer the claimable rewards to the user. In the following, we show the code snippets of the GaugeFeeDistributor::claimableTokens()/_claim() routines. As the name indicates, the GaugeFeeDistributor::claimableTokens() routine is intended to be a helper function for the user to query his/her claimable HOPE. It invokes the GaugeFeeDistributor::_claim() routine (line 287) to count the claimable amount. In the GaugeFeeDistributor::_claim() routine, it moves the user's claimed epoch and time cursor to the latest before returning the claimable amount (lines 267 268). However, the corresponding HOPE is not transferred to the user.

```solidity
function _claim(address gauge, address addr, uint256 _lastTokenTime) internal returns (uint256) {
    ClaimParam memory param;
    /// Minimal userEpoch is 0 (if user had no point)
    param.userEpoch = 0;
    param.toDistribute = 0;
    param.maxUserEpoch = IGaugeController(gaugeController).lastVoteVeLtPointEpoch(addr, gauge);
    uint256 startTime = startTime;
    if (param.maxUserEpoch == 0) { ... }
    param.weekCursor = timeCursorOf[gauge][addr];
    if (param.weekCursor == 0) {
        /// Need to do the initial binary search
        param.userEpoch = _findTimestampUserEpoch(gauge, addr, startTime, param.maxUserEpoch);
    } else
        param.userEpoch = userEpochOf[gauge][addr];
    if (param.userEpoch == 0)
        param.userEpoch = 1;
    param.userPoint = IGaugeController(gaugeController).voteVeLtPointHistory(addr, gauge, param.userEpoch);
    if (param.weekCursor == 0) {
        param.weekCursor = LibTime.timesRoundedByWeek(param.userPoint.ts + WEEK - 1);
        if (param.weekCursor >= _lastTokenTime)
            return 0;
    }
    if (param.weekCursor < startTime)
        param.weekCursor = startTime;
    param.oldUserPoint = Point({bias: 0, slope: 0, ts: 0, blk: 0});
    /// Iterate over weeks
    for (int i = 0; i < 50; i++) { ... }
    param.userEpoch = Math.min(param.maxUserEpoch, param.userEpoch - 1);
    userEpochOf[gauge][addr] = param.userEpoch;
    timeCursorOf[gauge][addr] = param.weekCursor;
    emit Claimed(gauge, addr, param.toDistribute, param.userEpoch, param.maxUserEpoch);
    return param.toDistribute;
}

function claimableTokens(address gauge, address _addr) external whenNotPaused returns (uint256) {
    if (_addr == address(0))
        _addr = msg.sender;
    uint256 _lastTokenTime = lastTokenTime;
    if (canCheckpointToken && (block.timestamp > _lastTokenTime + TOKEN_CHECKPOINT_DEADLINE))
        _checkpointToken();
    _lastTokenTime = block.timestamp;
    _lastTokenTime = LibTime.timesRoundedByWeek(_lastTokenTime);
    IGaugeController(gaugeController).checkpointGauge(gauge);
    return _claim(gauge, _addr, _lastTokenTime);
}
```

## Recommendation
Revisit the above GaugeFeeDistributor::claimableTokens() routine and properly transfer the claimed HOPE to the user or do not update user's claim state.
