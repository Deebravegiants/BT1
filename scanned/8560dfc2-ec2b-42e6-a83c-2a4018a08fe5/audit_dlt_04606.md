# [M] ``claimAndExitFor`` can be used to rug users

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/65
Type: sherlock-finding

## Details
imare

medium

# ``claimAndExitFor`` can be used to rug users

## Summary

As the comment in the code mentions the function ``claimAndExitFor`` should be used in case of a needed migration. But it can be easily used to rug users of the protocol.

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L454-L455


## Vulnerability Detail

``claimAndExitFor`` can be only called when protocol is paused. All other users when the protocol is in paused mode can't use the protocol (because ``whenNotPaused`` modifier is used on the main functions like ``exit``,``claim``). What is more important they cant withdraw their balances from the protocol.

But only the user/address with the role ``RECOVERY_ROLE`` can call ``claimAndExitFor`` function which allows only this user to pull out all founds from the protocol to an unknown address/contract.

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L457-L459

## Impact
Is not best practice to block users from their founds and having the ability to move their founds to another addresses.

## Code Snippet

## Tool used

Manual Review

## Recommendation
Instead of using ``claimAndExitFor`` for migrations. 

I would suggest to put the protocol in a migration state by providing the ability for the user to see where the found/accounts will be migrated.

Like having the owner of the protocol propose a migration address. Then accept this address after a lock period.

And then have **users by them selfs** call a new method like ``migrate`` to move their accounts (balances included) to the new implementation.
