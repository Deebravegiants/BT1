# [M] underflow with _timeHeldToIncrement 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-14
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/22
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
In the function _processRentCollection of RCMarket.sol a variable _timeHeldToIncrement is calculated by subtracting two timestamps.
This could have more or less any value.
Later on this is subtracted from cardTimeLimit and timeHeldLimit (see code below). The values of cardTimeLimit and timeHeldLimit will get closer to 0,
However its possible that the subtraction will "overshoot", which will lead to an underflow.
As solidity 8.x is used, a revert will occur and the code will stop.
This is probably not what is desired.

## Proof of Concept
// https://github.com/code-423n4/2021-06-realitycards/blob/main/contracts/RCMarket.sol#L854
function _collectRentAction(uint256 _card)
 uint256 _timeOfThisCollection = block.timestamp;
...
if ....    _timeOfThisCollection = marketLockingTime;
if .....   _timeOfThisCollection = _cardTimeLimitTimestamp;
if ....    _timeOfThisCollection = _timeUserForeclosed;
....
 _processRentCollection(_user, _card, _timeOfThisCollection); // where the rent collection actually happens

// https://github.com/code-423n4/2021-06-realitycards/blob/main/contracts/RCMarket.sol#L1052
function _processRentCollection(address _user,uint256 _card,uint256 _timeOfCollection) {
    ....
        uint256 _timeHeldToIncrement =  (_timeOfCollection - timeLastCollected[_card]);
     ....
            orderbook.reduceTimeHeldLimit(_user, _card, _timeHeldToIncrement);
            cardTimeLimit[_card] -= _timeHeldToIncrement;   // could underflow
        }

// https://github.com/code-423n4/2021-06-realitycards/blob/main/contracts/RCOrderbook.sol#L850
 function reduceTimeHeldLimit(address _user, uint256 _card, uint256 _timeToReduce ) external override onlyMarkets {
        user[_user][index[_user][msgSender()][_card]].timeHeldLimit -= SafeCast.toUint64(_timeToReduce);   // could underflow

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-06-realitycards-findings/issues/22_
