# [M] MultiInvoker closableAmount the calculation

## Summary
Severity: Medium
Contest weight: 0.7064
Dataset id: 20383
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In MultiInvoker._latest() the incorrect use of previousMagnitude = latestPosition.magnitude() has led to an error in the calculation of closableAmount. This has caused errors in judgments that use this variable, such as _liquidationFee(). There are currently multiple places where the user's closable needs to be calculated, such as market.update(). The calculation formula is as follows in the code: Market.sol
```solidity
function _processPendingPosition(Context memory context, Position memory newPendingPosition) private {
    context.pendingCollateral = context.pendingCollateral.sub(newPendingPosition.fee);
    context.closable = context.closable.sub(context.previousPendingMagnitude.sub(newPendingPosition.magnitude().min(context.previousPendingMagnitude)));
    context.previousPendingMagnitude = newPendingPosition.magnitude();
    if (context.previousPendingMagnitude.gt(context.maxPendingMagnitude))
        context.maxPendingMagnitude = newPendingPosition.magnitude();
}
```
It will loop through pendingPostion, and each loop will set the variable context.previousPendingMagnitude = newPendingPosition.magnitude(); to be used as the basis for the calculation of the next pendingPostion. closableAmount is also calculated in MultiInvoker._latest(). The current implementation is as follows:
```solidity
function _latest(
    IMarket market,
    address account
) internal view returns (
    uint256 latestPrice,
    Position memory latestPosition,
    uint256 closableAmount
) {
    // load latest price
    OracleVersion memory latestOracleVersion = market.oracle().latest();
    latestPrice = latestOracleVersion.price;
    IPayoffProvider payoff = market.payoff();
    if (address(payoff) != address(0)) latestPrice = payoff.payoff(latestPrice);

    // load latest settled position
    uint256 latestTimestamp = latestOracleVersion.timestamp;
    latestPosition = market.positions(account);
    closableAmount = latestPosition.magnitude();
    // scan pending position for any ready-to-be-settled positions
    Local memory local = market.locals(account);
    for (uint256 id = local.latestId + 1; id <= local.currentId; id++) {
        // load pending position
        Position memory pendingPosition = market.pendingPositions(account, id);

        pendingPosition.adjust(latestPosition);
        // virtual settlement
        if (pendingPosition.timestamp <= latestTimestamp) {
            if (!market.oracle().at(pendingPosition.timestamp).valid)
                latestPosition.invalidate(pendingPosition);
            latestPosition.update(pendingPosition);
            previousMagnitude = latestPosition.magnitude();
            closableAmount = previousMagnitude;
            // process pending positions
        } else {
            closableAmount = closableAmount.sub(previousMagnitude.sub(pendingPosition.magnitude().min(previousMagnitude)));
            previousMagnitude = latestPosition.magnitude();
        }
    }
}
```
This method also loops through pendingPosition, but incorrectly uses latestPosition.magnitude() to set previousMagnitude, previousMagnitude = latestPosition.magnitude();. The correct way should be previousMagnitude = currentPendingPosition.magnitude() like market.sol. This mistake leads to an incorrect calculation of closableAmount. The calculation of closableAmount is incorrect, which leads to errors in the judgments that use this variable, such as _liquidationFee().

## Recommendation
```solidity
function _latest(
    IMarket market,
    address account
) internal view returns (
    uint256 latestPrice,
    Position memory latestPosition,
    uint256 closableAmount
) {
    // load latest price
    OracleVersion memory latestOracleVersion = market.oracle().latest();
    latestPrice = latestOracleVersion.price;
    IPayoffProvider payoff = market.payoff();
    if (address(payoff) != address(0)) latestPrice = payoff.payoff(latestPrice);

    // load latest settled position
    uint256 latestTimestamp = latestOracleVersion.timestamp;
    latestPosition = market.positions(account);
    closableAmount = latestPosition.magnitude();
    // scan pending position for any ready-to-be-settled positions
    Local memory local = market.locals(account);
    for (uint256 id = local.latestId + 1; id <= local.currentId; id++) {
        // load pending position
        Position memory pendingPosition = market.pendingPositions(account, id);

        pendingPosition.adjust(latestPosition);
        // virtual settlement
        if (pendingPosition.timestamp <= latestTimestamp) {
            if (!market.oracle().at(pendingPosition.timestamp).valid)
                latestPosition.invalidate(pendingPosition);
            latestPosition.update(pendingPosition);
            previousMagnitude = latestPosition.magnitude();
            closableAmount = previousMagnitude;
            // process pending positions
        } else {
            closableAmount = closableAmount.sub(previousMagnitude.sub(pendingPosition.magnitude().min(previousMagnitude)));
            previousMagnitude = pendingPosition.magnitude();
        }
    }
}
```
