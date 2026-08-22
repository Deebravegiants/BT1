# [M] SpendProofV1 txid-substitution: get_spend_proof/check_spend_proof do not verify returned transaction hash

## Summary
Severity: Medium (CVSS 5.3)
Program: Monero
Weakness: Missing Required Cryptographic Step
Reporter: bebensap
State: resolved
Disclosed: 2026-08-05T10:23:21.523Z
Source: https://hackerone.com/reports/3700036

## Details
**Repository:** [`monero-project/monero`](https://github.com/monero-project/monero) — `src/wallet/wallet2.cpp`. Snapshot: `master @ 3ad4a5ee8` (`v0.18.1.0-3ad4a5ee8`).

## Summary

Both helpers fetch a pruned transaction with `/gettransactions`, parse it with `get_pruned_tx()`, then build the spend-proof challenge from the **`txid` argument**, not from the hash implied by the blob. Neither compares `tx_hash` (from parsing) to `txid` before signing or verifying. `check_tx_proof()` on the same RPC path does that comparison.

`get_spend_proof` (roughly `wallet2.cpp` 11868–11969): request, parse, then:

```cpp
std::string sig_prefix_data((const char*)&txid, sizeof(crypto::hash));
sig_prefix_data += message;
crypto::hash sig_prefix_hash;
crypto::cn_fast_hash(sig_prefix_data.data(), sig_prefix_data.size(), sig_prefix_hash);
// ring sigs use tx / rings from res.txs[0], not a second hash check
```

`check_spend_proof` (same file, ~11979–12084) repeats the pattern: prefix hash from `txid`, ring checks from the parsed `tx`.

For comparison, after `get_pruned_tx` in `check_tx_proof`:

```cpp
THROW_WALLET_EXCEPTION_IF(tx_hash != txid, error::wallet_internal_error,
    "Failed to get the right transaction from daemon");
```

So if the HTTP peer in front of the wallet is malicious (fake `monerod`, corporate proxy, or on-path MITM), it can answer a request for txid **B** with a valid serialized body for a different tx **A**. The wallet still signs `H(B || message)` while using inputs/key images/rings from **A**. Verifiers that use `check_spend_proof` against the same bad endpoint will see `good: true` for **B** even though nothing in the response actually authenticates **B**.

This is integrity of the spend proof binding, not key exfiltration or remote wallet compromise. You still need a broken or attacker-controlled daemon channel.

## Releases Affected

Re-checked on `master @ 3ad4a5ee8`. The missing `tx_hash == txid` guard is plain in source; any branch with this spend-proof code path behaves the same unless someone already merged an equivalent check.

## Steps to Reproduce

The practical check is end-to-end: real `monerod --regtest`, real `monero-wallet-rpc`, and a tiny Python reverse proxy that forwards to the honest node but, on `POST /gettransactions`, replaces a chosen **FAKE** `txs_hashes` entry with the **REAL** hash of a spend the wallet actually made. The node returns a consistent pruned tx for **A**; the RPC still asks for a proof on **FAKE**. No Monero source edits.

**One command (paths match this machine; adjust `MONERO_BUILD` if your tree lives elsewhere):**

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3700036_
