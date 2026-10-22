# [M] Incorrect Logic in unclaimedTeamFund()

## Summary
Severity: Medium
Contest weight: 0.4279
Dataset id: 11545
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Orcus protocol has the built-in tokenomics that distribute the protocol tokens ORU to various ecosystem members. While analyzing the token distribution logic, we notice the current implementation needs to be improved. To elaborate, we show below this helper routine from the ORU token contract. This unclaimedTeamFund() routine is designed to compute the unclaimed fund that can be claimed by the team. It comes to our attention that the routine always makes use of the current emissionRate, without considering the possibility where the elapsed time may cross multiple years, which require the use of respective emissionRate on each year!
```solidity
function unclaimedTeamFund() public view returns (uint256) {
    uint256 _now = block.timestamp;
    if (_now <= teamVesting.lastClaimed) {
        return 0;
    }
    uint256 _fromEpoch = _now - teamVesting.startTime;
    uint256 _years = _fromEpoch / ONE_YEAR;
    uint256 _emissionRate = TEAM_FUND_EMISSION_RATE;
    for (uint256 i = 0; i < _years; i++) {
        _emissionRate = (_emissionRate * VESTING_DECREASING_RATIO) / RATIO_PRECISION;
    }
    uint256 _timeElapsed = _now - teamVesting.lastClaimed;
    uint256 _available = Math.min(
        _timeElapsed * _emissionRate,
        TEAM_FUND_ALLOCATION - teamVesting.vestedAmount
    );
    return _available;
}
```

## Recommendation
Revise the above unclaimedTeamFund() routine to properly compute the funds that can be claimed by the team. Note the same issue is also applicable to another contract OrcusV1Distributor.
