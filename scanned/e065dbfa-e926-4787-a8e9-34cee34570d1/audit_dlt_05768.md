# [M] ZeroLockermerge can make a voting lock last lon...

## Summary
Severity: Medium
Chain: Smart contract
Component: ZeroLend
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28892%20-%20%5BSC%20-%20Medium%5D%20ZeroLockermerge%20can%20make%20a%20voting%20lock%20last%20lon....md
Type: immunefi-boost

## Details
Target: https://github.com/zerolend/governance

## Description

I have previously reported an issue called "ZeroLocker:merge can make a voting lock last longer than 4 years" as a primary medium-severity issue at Cantina's contest as there wasn't a voting power calculation function at that codebase. I am reporting it again as the impact at the codebase in Immunefi's scope is higher and presents a significance for the voting mechanics.

## Brief/Intro

The BaseLocker contract allows users to merge two different locks and end up with a lock that has a longer than MAXTIME difference between the end time and start time. This inflates the calculation of voting power for locks and give them an unfair advantage on governance.

## Vulnerability Details

The merge method enables a user to bypass the MAXTIME requirement by creating two different locks that last MAXTIME, one at Time0 and the second one some time later at Time1 then merging with the first lock as the merge target (or **to** argument) at the merge call:

```solidity
function merge(uint256 _from, uint256 _to) external override {
```

As the merge function at the BaseLocker contract does not check whether the end minus the locked0.start is not greater than MAXTIME, it enables arbitrary-sized lock durations:

```solidity
LockedBalance memory _locked0 = locked[_from];
        LockedBalance memory _locked1 = locked[_to];
        uint256 value0 = uint256(int256(_locked0.amount));
        uint256 end = _locked0.end >= _locked1.end
            ? _locked0.end
            : _locked1.end;

        locked[_from] = LockedBalance(0, 0, 0, 0);

        _burn(_from);
        _depositFor(_to, value0, end, _locked1, DepositType.MERGE_TYPE);
```

The depositFor internal method updates the lock, but it doesn't check the end timestamp and the start timestamp difference either, the only sanity check is in regards to unlockTime != 0:

```solidity
if (_unlockTime != 0) lock.end = _unlockTime;
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28892%20-%20%5BSC%20-%20Medium%5D%20ZeroLockermerge%20can%20make%20a%20voting%20lock%20last%20lon....md_
