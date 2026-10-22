# [M] DrawManager.canStartDraw does not consider

## Summary
Severity: Medium
Contest weight: 0.4620
Dataset id: 22840
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inconsistent checks in the DrawManager.canStartDraw function, neglecting to consider retried RNG requests, might lead to wrongly assuming that a new draw auction cannot be started.
The DrawManager.canStartDraw function checks if the startDraw function can be called. However, the checks are not consistent with the startDraw function.
Specifically, the check in line 289 to determine if the draw has expired is different than the auction duration check in the startDraw function in lines 250-251. The latter uses the last RNG request's closedAt timestamp to determine the elapsed auction time, to consider any retried failed RNG requests, while the former checks if the draw has expired, not considering retried RNG requests.
As a result, if for a given draw a RNG request has been retried, and thus the total elapsed time from the draw close until now (block.timestamp) might exceed the auction duration, off-chain actors calling the canStartDraw function might wrongly assume that the draw auction can not be started, even though such a call would succeed.
As canStartDraw is also called internally by the startDrawReward function and both functions are likely to be used by off-chain actors to determine if a new draw auction an be started, this might lead to wrongly assuming that a new draw auction cannot be started, even though it should be possible. As a result, the current draw might not get awarded.
DrawManager.canStartDraw()
```solidity
/// @notice Checks if the start draw can be called.
/// @return True if start draw can be called, false otherwise
function canStartDraw() public view returns (bool) {
    uint24 drawId = prizePool.getDrawIdToAward();
    uint48 drawClosesAt = prizePool.drawClosesAt(drawId);
    StartDrawAuction memory lastStartDrawAuction = getLastStartDrawAuction();
    return (
        (
            // if we're on a new draw
            drawId != lastStartDrawAuction.drawId ||
            // OR we're on the same draw, but the request has failed and we haven't retried too many times
            (rng.isRequestFailed(lastStartDrawAuction.rngRequestId) && _startDrawAuctions.length <= maxRetries)
        ) && // we haven't started it, or we have and the request has failed
        block.timestamp >= drawClosesAt && // the draw has closed
        _computeElapsedTime(drawClosesAt, block.timestamp) <= auctionDuration // the draw hasn't expired
    );
}
```

## Recommendation
Consider using the last request's closedAt timestamp instead of drawClosesAt to determine if the auction has expired to consider failed RNG requests that have been retried by calling startDraw again.
