# [M] Users can front-run StakingModule.slash

## Summary
Severity: Medium
Reporter: cccz
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L403-L406
Type: audit-issue

## Details
# Users can front-run StakingModule.slash

## Summary
When SLASHER_ROLE calls StakingModule.slash to slash the user, the user can preemptively call fullClaimAndExit to prevent being slashed.
## Vulnerability Detail
In the StakingModule contract, SLASHER_ROLE can call the slash function to slash the user, but since the user can call the fullClaimAndExit function to exit at any time (except when the contract is paused, and the user can also front-run the pause function), which allows the user to front-run the slash function to prevent being slashed.
## Impact
Users can front-run the slash function to prevent being slashed.
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L403-L406
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L202-L207
## Tool used

Manual Review

## Recommendation
Consider adding a lock-up period to the user's stake, thus preventing the user from exiting when they are slashed.
