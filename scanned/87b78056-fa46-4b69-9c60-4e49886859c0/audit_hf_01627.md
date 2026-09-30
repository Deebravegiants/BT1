# [M] User's position might be bricked when an LRT is removed

## Summary
Severity: Medium
Contest weight: 0.5386
Dataset id: 8739
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When an LRT is removed using the CvToken::removeLrtProtocol() function, but some users still have deposits of that token, their positions will become inaccessible due to the following check in the getLRTUnderlyingValue() function. This check is triggered while calculating the health of a user's position through the getUserLoanInfo() function:
```solidity
if (protocol == address(0)) {
    revert Errors.ProtocolNotFound(lrt);
}
```

## Recommendation
Modify getUserLoanInfo() to skip removed assets while calculating a user's loan info, as shown below:
```solidity
if (userDeposit.amount == 0 || lrtToConfig[userDeposit.lrt].protocol == address(0)) {
    continue;
}
```
