# [M] proper validation should be done on addPlugin function

## Summary
Severity: Medium
Reporter: silviaxyz
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417
Type: audit-issue

## Details
# proper validation should be done on addPlugin function

## Summary
Without validation for new plugin address in addPlugin(), wrong address can be added.

## Vulnerability Detail
When adding new plugin, there is no validation for the address besides the existing plugin check.

## Impact
Adding correct plugin is quite essential for this contract. Without proper validations this contract wouldn't work correctly. Even for existing plugins adding it with wrong address as a new plugin will cause error on supply etc. 

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417

## Tool used

Manual Review

## Recommendation
Validate existing plugin addresses, validate address
