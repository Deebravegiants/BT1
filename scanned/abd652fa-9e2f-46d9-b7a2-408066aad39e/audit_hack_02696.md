# [M] Setter in VaultAdmin need time lock

## Summary
Severity: Medium
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L28-L190
Type: audit-issue

## Details
# Setter in VaultAdmin need time lock

## Summary

In VaultAdmin.sol, all the setter functions can take effects immediately, leaving users or the owners no time to react in case of abrupt change.
Some users might need to make decisions based on some parameters, such as the fee, or delta/offset value.
In case of the owner being compromised, time lock also serve as a buffer to take emergency actions.

## Vulnerability Detail

When critical parameters of systems need to be changed, it is required to broadcast the change via event emission and recommended to enforce the changes after a time-delay. This is to allow system users to be aware of such critical changes and give them an opportunity to exit or adjust their engagement with the system accordingly. None of the onlyOwner functions that change critical protocol addresses/parameters have a timelock for a time-delayed change to alert: 
- users and give them a chance to engage/exit protocol if they are not agreeable to the changes 
- team in case of compromised owner(s) and give them a chance to perform incident response.
- for some parameters, like `startOffset` and `endOffset`, if changed immediately before the auction, users have no enough time to react to the changes. It would be more appropriate to delay to the next auction.

Users may be surprised when critical parameters are changed. Furthermore, it can erode users' trust since they can’t be sure the protocol rules won’t be changed later on. Compromised owner keys may be used to change protocol addresses/parameters to benefit attackers. Without a time-delay, authorized owners have no time for any planned incident response. (May be medium since owner can change critical parameters at anytime that can affect the users poorly).



## Impact

- Some users might need to make decisions based on some parameters, such as the fee, or delta/offset value. Sudden changes of the parameter values could make users strategy ineffective and lose fund
- In case of the owner being compromised, time lock also serve as a buffer to take emergency actions.

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L28-L190

## Tool used

Manual Review


## Recommendation

Add time lock for the setter functions in VaultAdmin.sol.
