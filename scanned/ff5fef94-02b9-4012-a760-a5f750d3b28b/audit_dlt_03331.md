# [M] [WP-H9] Centralization Risk: Funds can be frozen when critical key holders lose access to their keys

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-sandclock
Published: 2022-01-12
Source: https://github.com/code-423n4/2022-01-sandclock-findings/issues/165
Type: code-finding

## Details
# Handle

WatchPug


# Vulnerability details

The current implementation requires trusted key holders (`isTrusted[msg.sender]`) to send transactions (`initRedeemStable()`) to initialize withdrawals from `EthAnchor` before the users can withdraw funds from the contract.

https://github.com/code-423n4/2022-01-sandclock/blob/a90ad3824955327597be00bb0bd183a9c228a4fb/sandclock/contracts/strategy/BaseStrategy.sol#L214-L223

https://github.com/code-423n4/2022-01-sandclock/blob/a90ad3824955327597be00bb0bd183a9c228a4fb/sandclock/contracts/strategy/BaseStrategy.sol#L163-L170

This introduces a high centralization risk, which can cause funds to be frozen in the contract if the key holders lose access to their keys.

## PoC

Given:

- `investPerc` = 80%
- 1,000 users deposited 1M UST in total ($1000 each user in avg), 800k invested into AUST (`EthAnchor`)

If the key holders lose access to their keys ("hit by a bus"). The 800k will be frozen in `EthAnchor` as no one can `initRedeemStable()`.

## Recommendation

See the recommendation on issue [WP-M1].
