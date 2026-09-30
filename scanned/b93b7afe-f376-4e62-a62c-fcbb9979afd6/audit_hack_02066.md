# [M] 7.5 Everybody Can Pause Pools

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 2 Code Corrected

In the second version of the code, a pool will be paused, if during a user's burn, the amount of AgTokens
to be burned is higher than the stocks users of the collateral. However, there is no check whether the
user actually owns the necessary amount of AgTokens. Thus, any user can specify a high amount to
burn to pause the contract. The pool will remain paused until the governance unpauses this change.
Malicious parties could act as follows:

- Stableholders: In case of expected collateral price drop can pause to make HAs and SLPs lose.
- SLPs: A SLP providing much liquidity in a state with much HA capital could pause the contract to
    keep other SLPs from entering the protocol so that his profit is maximized.
- HAs: HAs can front-run liquidations and force-cashouts by pausing the contract. Ultimately, that
    could lead to a highly unbalanced state.

In conclusion, anybody can pause the protocol at any time. Such actions could be profitable for the
parties and could throw the system into an unhealthy state if they are executed repeatedly.

Code corrected:

When the amount of AgTokens burned exceeds the stocksUsers, the transaction reverts instead of
pausing the contracts.
