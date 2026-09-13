# [M] eth_subscribe over WebSocket allows unbounded subscription creation, growing SubscriptionManager's in-memory state without limit

## Summary
Severity: Medium
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-14
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-ffqr-pj4h-xq37
Type: github-advisory

## Details
A client could open eth_subscribe WebSocket subscriptions indefinitely, growing SubscriptionManager's in-memory state without bound. This is CertiK finding HYB-03 (Medium). Fixed by adding a configurable cap on globally-active subscriptions (--rpc-ws-max-active-subscriptions, default 100,000, 0 = no limit) enforced at subscribe time, returning EXCEEDS_RPC_MAX_ACTIVE_SUBSCRIPTIONS once the cap is hit; subscriptions belonging to a connection are also now cleaned up if the connection closes mid-subscribe. Fixed in Besu 26.7.1 by commit 3f14a9b561106e9dff3c58ac9d79ba9a99326af0 (besu-eth/besu PR #10894). Websockets feature is disabled by default.
