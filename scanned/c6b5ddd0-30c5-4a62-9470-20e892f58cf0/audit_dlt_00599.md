# [?] Fix custody context initialization race condition that caused panic (#8391)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-11-17
Source: https://github.com/sigp/lighthouse/commit/af1d9b99911e2467a56ce9f308f06ec7a9ead3eb
Type: security-commit

## Details
Fix custody context initialization race condition that caused panic (#8391)

Take 2 of #8390.

Fixes the race condition properly instead of propagating the error. I think this is a better alternative, and doesn't seem to look that bad.


  * Lift node id loading or generation from `NetworkService ` startup to the `ClientBuilder`, so that it can be used to compute custody columns for the beacon chain without waiting for Network bootstrap.

I've considered and implemented a few alternatives:
1. passing `node_id` to beacon chain builder and compute columns when creating `CustodyContext`. This approach isn't good for separation of concerns and isn't great for testability
2. passing `ordered_custody_groups` to beacon chain. `CustodyContext` only uses this to compute ordered custody columns, so we might as well lift this logic out, so we don't have to do error handling in `CustodyContext` construction. Less tests to update;.


Co-Authored-By: Jimmy Chen <jchen.tc@gmail.com>
