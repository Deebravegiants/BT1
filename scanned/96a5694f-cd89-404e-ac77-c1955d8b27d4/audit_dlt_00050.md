# [M] getblock verbosity 2 on a side-chain block panics the node via negative-confirmations u32 conversion

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-03
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-x6v8-c2xp-928m
Type: github-advisory

## Details
## Am I affected?

You are affected if you run an affected version and expose the `getblock` RPC to untrusted input, directly or indirectly. `getblock` is one of the methods lightwalletd forwards, so a node serving a lightwalletd instance is reachable from lightwalletd clients. A node with the RPC port exposed without cookie authentication is reachable directly. The crash requires only a `getblock` call with verbosity 2 against a block hash that is in the node's state but not on the best chain (a side-chain block).

## Summary

In the verbosity-2 arm of `get_block`, the per-transaction object is built by converting the block's `confirmations` value into a `u32` with `.expect()`. For a block that is not on the best chain, `confirmations` is the sentinel `-1`. Converting `-1i64` into `u32` fails, the `.expect()` panics, and because the workspace sets `panic = "abort"`, the entire node process aborts. An attacker who can reach `getblock` (including through lightwalletd) can crash the node by calling `getblock <side-chain-hash> 2`, and can keep it down by repeating the call.

## Details

Verified on v5.2.0.

The verbosity-2 arm of `get_block` builds each transaction object as follows (`zebra-rpc/src/methods.rs:1338-1342`):

```rust
TransactionObject::from_transaction(
    tx.clone(),
    Some(height),
    Some(confirmations.try_into().expect(
        "should be less than max block height, i32::MAX",
    )),
    // ...
)
```

`TransactionObject::from_transaction` takes `confirmations: Option<u32>` (`zebra-rpc/src/methods/types/transaction.rs:797`), so the `i64` confirmations value is narrowed to `u32` here.

The `confirmations` value originates as an `i64` and is set to a negative sentinel for any block not on the best chain (`zebra-rpc/src/methods.rs:1508-1514`):

```rust
const NOT_IN_BEST_CHAIN_CONFIRMATIONS: i64 = -1;
// ...
let confirmations = depth
    .map(|depth| i64::from(depth) + 1)
    .unwrap_or(NOT_IN_BEST_CHAIN_CONFIRMATIONS);
```

For a side-chain block, `depth` is `None`, so `confirmations` is `-1`. The block header object carries this `-1` as `i64` without trouble. The verbosity-2 transaction path instead converts it to `u32`: `(-1i64).try_into::<u32>()` returns `Err`, and the `.expect()` panics. The workspace sets `panic = "abort"` (`Cargo.toml`), so the panic aborts the process rather than unwinding the task.

The block hash is fully attacker-controlled. Side-chain blocks occur naturally after any reorg, and an attacker can feed a short competing chain to guarantee one exists in the node's state.

## Impact

A remote, unauthenticated caller (directly, or through lightwalletd) can crash the node with a single `getblock <side-chain-hash> 2` call, and can hold the node down with a crash loop by repeating the call. There is no state corruption, no consensus impact, and no persistence: the node recovers on restart. The impact is availability only, which is why this is rated Medium rather than High.

## Patches
11.0.0

## Workarounds

Keep RPC cookie authentication enabled and do not expose the RPC port to untrusted networks. Note this does not protect against reports forwarded through lightwalletd, since lightwalletd forwards `getblock`; upgrading once a patch is available is the durable fix.

## Credit

Reported by the Mythos (Anthropic CVD) audit, via Taylor Hornby (finding 155RKT4Y), with an accurate root-cause analysis and reproduction.

## References

- `zebra-rpc/src/methods.rs:1338-1342` (verbosity-2 conversion / panic site)
- `zebra-rpc/src/methods.rs:1508-1514` (NOT_IN_BEST_CHAIN_CONFIRMATIONS sentinel)
- `zebra-rpc/src/methods/types/transaction.rs:797` (`confirmations: Option<u32>`)
