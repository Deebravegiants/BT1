# [?] accounts: fix data race when closing manager (#31982)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-06-17
Source: https://github.com/ethereum/go-ethereum/commit/2e6d978e3573e22dc0fe91b9e7a8b2e0043835ab
Type: security-commit

## Details
accounts: fix data race when closing manager (#31982)

Fixes a data race on the `wallets` slice when closing account Manager.

At the moment, there is a data race between a go-routine calling the
Manager's `Close` function and the background go-routine handling most
operations on the `Manager`. The `Manager`'s `wallets` field is accessed
without proper synchronization.

By moving the closing of wallets from the `Close()` function into the
background thread, this issue can be resolved.
