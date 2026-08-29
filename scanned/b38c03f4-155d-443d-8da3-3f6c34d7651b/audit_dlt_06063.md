# [?] Avoid tcp channel close deadlock (#5079)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-06-08
Source: https://github.com/nanocurrency/nano-node/commit/96aa784aecc0242157985579a937bc7075fa2b59
Type: security-commit

## Details
Avoid tcp channel close deadlock (#5079)

* Avoid tcp channel close deadlock

Swap the channel set out from under tcp_channels::mutex before closing entries. This avoids holding the mutex while close paths block on io_context shutdown.

* Avoid mutex nesting in bootstrap maintenance

Rename the cleanup loop and thread to maintenance since it now handles broader periodic work. Snapshot bootstrap channels without holding the bootstrap mutex before syncing peer scoring, avoiding network mutex nesting under the bootstrap lock.
