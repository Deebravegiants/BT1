# [M] Full node denial of service via crafted Sapling receiver in z_listunifiedreceivers

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CWE: Improper Input Validation, Uncaught Exception, Reachable Assertion, Improper Check for Unusual or Exceptional Conditions
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-c8w6-x74f-vmg3
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your `zebrad.toml` sets `rpc.listen_addr` to a TCP address (RPC server is enabled).
3. An attacker can authenticate to the RPC endpoint. With the default `enable_cookie_auth = true`, this requires the attacker to read the `.cookie` file (typically local access). With `enable_cookie_auth = false`, any network client reaching the RPC port can trigger it.

### Summary

The `z_listunifiedreceivers` RPC handler panics when processing a structurally valid Unified Address whose Sapling receiver carries 43 bytes that fail cryptographic validation (`sapling_crypto::PaymentAddress::from_bytes` returns `None` for non-subgroup Jubjub points). The handler calls `.expect("using data already decoded as valid")` on the fallible result. Because Zebra's release profile sets `panic = "abort"`, the panic terminates the entire node process, not just the RPC task.

### Details

`zcash_address::unified::Encoding::decode` validates only the structural envelope of a Unified Address (F4Jumble, bech32m, typecode ordering, 43-byte length for Sapling). It does not validate that the embedded `pk_d` is a valid Jubjub subgroup point or that the diversifier produces a valid `g_d` preimage.

At `zebra-rpc/src/methods.rs:2893`, the handler calls `Address::try_from_sapling(network, data)`, which delegates to `sapling_crypto::PaymentAddress::from_bytes`. When `from_bytes` returns `None` (most random 32-byte strings fail the subgroup check), the `.expect()` fires and the process aborts.

The same crate already handles this correctly in `try_from_unified` at `zebra-chain/src/primitives/address.rs:99-110`, which returns `Err` when `from_bytes` fails. The vulnerable code path bypasses this validated route.

### Patches

TBD.

Replace `.expect()` with `.map_err(|e| ErrorObject::owned(...))` for proper error propagation, or route through the existing `try_from_unified` path which already handles this case correctly.

### Workarounds

- Disable the RPC server by removing `rpc.listen_addr` from `zebrad.toml`.
- Ensure `enable_cookie_auth = true` (the default) and restrict filesystem access to the `.cookie` file.
- Place a reverse proxy in front of the RPC port that rejects `z_listunifiedreceivers` calls with untrusted address parameters.

### Impact

A single authenticated RPC request terminates the `zebrad` process. The attack is repeatable on restart (the same request triggers the same abort), allowing an attacker to keep the node down indefinitely until the request is filtered upstream. Operators using `lightwalletd` backends, Zaino indexers, or mining pool infrastructure that forward RPC calls to `zebrad` may be exposed if the forwarding path passes through `z_listunifiedreceivers`.

### Credit


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-c8w6-x74f-vmg3_
