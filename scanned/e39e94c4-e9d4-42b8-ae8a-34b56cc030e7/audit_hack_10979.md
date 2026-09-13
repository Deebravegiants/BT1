# [M] _mint and _burn are open to the public

## Summary
Severity: Medium
Reporter: Delvir0
Source: https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/USSD.sol#L204-L210
Type: audit-issue

## Details
# _mint and _burn are open to the public

## Summary
Missing AC on two functions
## Vulnerability Detail
https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/USSD.sol#L204-L210
Above both do not have any AC or checks in place, meaning anyone can mint and burn to or from this contract as they please
## Impact
Completely mess the contracts accounting and supply
## Code Snippet
Mentioned above
## Tool used

Manual Review

## Recommendation
Implement checks or AC
