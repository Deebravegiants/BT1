# [?] event: fix Resubscribe deadlock when unsubscribing after inner sub ends (#28359)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-10-22
Source: https://github.com/etclabscore/core-geth/commit/ffc6a0f36edda396a8421cf7a3c0feb88be20d0b
Type: security-commit

## Details
event: fix Resubscribe deadlock when unsubscribing after inner sub ends (#28359)

A goroutine is used to manage the lifetime of subscriptions managed by
resubscriptions. When the subscription ends with no error, the resub
goroutine ends as well. However, the resub goroutine needs to live
long enough to read from the unsub channel. Otheriwse, an Unsubscribe
call deadlocks when writing to the unsub channel.

This is fixed by adding a buffer to the unsub channel.
