# [M] Revisited Logic in BitcoinEarningsOracle

## Summary
Severity: Medium
Contest weight: 0.5938
Dataset id: 12506
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the RiskControl contract, the issuer delivers mining earnings to users to unlock the funds. The mining earnings of each day is obtained from the BitcoinEarningsOracle contract. While examining the logic to update the daily earnings in the BitcoinEarningsOracle contract, we notice the meaning of the day index is inconsistent with what it is expected in the RiskControl contract. To elaborate, we show below the code snippets from the BitcoinEarningsOracle/RiskControl contracts. As the name indicates, the trackDailyEarnings() routine is used for the TRACK_ROLE to update the daily earnings. Note the day here (line 69) indicates the days since the epoch time (line 62). However, in the RiskControl::deliver() routine where the daily earnings are queried, the provided desDay (line 149) means the days since the end of the collection period (lines 135–136). The inconsistency between the meanings of the day index makes the returned daily earnings unexpected.
```solidity
function _today() private view returns (uint256) {
    return block.timestamp / 1 days;
}
function trackDailyEarnings(
    uint256[] memory earnings_,
    uint256[] memory hashrates_
) public onlyRole(TRACK_ROLE) {
    uint256 day = _today();
    _makerDailyEarnings(day, earnings_, hashrates_);
    emit TrackDailyEarnings(day, _dailyEarnings[day]);
}
function dayNow() public view override returns (uint256) {
    require(
        _currentStage() > Stage.CollectionPeriod,
        "RiskControl: error stage"
    );
    uint256 duration = block.timestamp - (startTime + collectionPeriodDuration);
    return duration / 1 days;
}
function deliver() public {
    require(
        deliverAllowed() && dayNow() > 0,
        "RiskControl: deliver not allowed"
    );
    require(
        initialPayment != 0 && _currentStage() == Stage.ObservationPeriod,
        "RiskControl: must generate initial payment"
    );
    uint256 desDay = dayNow() - 1;
    require(deliverRecords[desDay] == 0, "RiskControl: already deliver");
    uint256 earnings = earningsOracle.getRound(desDay);
    if (earnings == 0) {
        (, uint256 lastEarnings) = earningsOracle.lastRound();
        earnings = lastEarnings;
    }
    ...
}
```
What is more, in the BitcoinEarningsOracle::getRound() routine, which is used in the RiskControl::deliver() routine to get the earnings for the input day, it reverts the transaction (line 48) if the daily earnings are not set. That is to say it is impossible for the routine to return 0. However, in the RiskControl::deliver() routine, it has a special handling when the returned earning is 0 (line 152) which could never be reached. Our analysis shows that the BitcoinEarningsOracle::getRound() routine shall return 0 if the daily earnings are not set.
```solidity
function getRound(uint256 day) public view virtual override returns (uint256) {
    for (uint256 i = 0; i < 7; ++i) {
        uint256 earning = _dailyEarnings[day - i];
        if (earning != 0) {
            return earning;
        }
    }
    revert("!round");
}
```

## Recommendation
Revisit the above mentioned logic in the BitcoinEarningsOracle contact to make it consistent with the using from the RiskControl contact.
