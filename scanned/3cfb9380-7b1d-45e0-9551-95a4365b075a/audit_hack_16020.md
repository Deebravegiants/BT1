# [M] need overflow check

## Summary
Severity: Medium
Reporter: Expert Teal Dragon
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# need overflow check
There is no overflow check at `QVBaseStrategy._qv_allocate`

## Vulnerability Detail
Following lines can easily lead to an overflow if `totalCredits` is large enough.

```
        uint256 voteResult = _sqrt(totalCredits * 1e18);
```


## Impact

`voteResult` will revert protocol can't be used.

## Code Snippet

## Tool used

Manual Review

## Recommendation
set max value for voteResult
