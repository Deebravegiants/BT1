# [M] `emitForWeek` will lose `emissionForWeek` if one week is skipped

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1218
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/TapOFT.sol#L207-L208


# Vulnerability details

`emitForWeek` has a mechanism to bring over unclaimed emissions from the previous week:
https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/TapOFT.sol#L207-L208

```solidity
uint256 unclaimed = emissionForWeek[week - 1] - mintedInWeek[week - 1];
uint256 emission = uint256(_computeEmission());
```
`emitForWeek` is `pausable`, meaning that a week may be skipped.

In that case, the unclaimedEmissions from the previous week, would result in a zero.

That would cause the previous emissions to no longer being claimable

### POC

The POC is coded with Foundry and compares the result of skipping a week vs claiming 0 on that week

#### Skipping a Week
```python
[PASS] testSkipAWeek() (gas: 142286)
Logs:
  week1 469157964000000000000000
  week2 465029373916800000000000
  week4 465029373916800000000000
```
#### Not Claiming for a week
```python
[PASS] testNoSkip() (gas: 165882)
Logs:
  week1 469157964000000000000000
  week2 465029373916800000000000
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1218_
