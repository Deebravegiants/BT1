# [M] `check_reserve_proof` counts duplicate entries: one output can inflate `total`

## Summary
Severity: Medium (CVSS 4.8)
Program: Monero
Weakness: Business Logic Errors
Reporter: bebensap
State: resolved
Disclosed: 2026-08-05T10:23:55.815Z
Source: https://hackerone.com/reports/3699522

## Details
**Repository:** [`monero-project/monero`](https://github.com/monero-project/monero) — `src/wallet/wallet2.cpp`, `src/wallet/wallet_rpc_server.cpp`. Snapshot: `master @ 3ad4a5ee8` (`v0.18.1.0-3ad4a5ee8`).

## Summary

Reserve proofs are untrusted blobs. The verifier walks a vector of `reserve_proof_entry` and, for each row, checks signatures against a prefix hash, then adds that row’s output amount to `total` (and `spent` when the daemon says the key image is spent). Nothing in that loop requires each `key_image` or each `(txid, index_in_tx)` to appear only once.

The prefix is built by concatenating the message, the claimed address, and every `key_image` in order—the same layout the honest `get_reserve_proof` uses:

```cpp
std::string prefix_data = message;
prefix_data.append((const char*)&address, sizeof(cryptonote::account_public_address));
for (size_t i = 0; i < proofs.size(); ++i)
  prefix_data.append((const char*)&proofs[i].key_image, sizeof(crypto::key_image));
crypto::hash prefix_hash;
crypto::cn_fast_hash(prefix_data.data(), prefix_data.size(), prefix_hash);
```

If you repeat the same output N times in `proofs`, you also repeat N copies of that key image in `prefix_data`, recompute `prefix_hash`, and sign against that hash. The owner of the output already has the keys to produce valid `shared_secret_sig` and `key_image_sig` for each row; those checks are per-row and do not see “this key image was already used.”

The accounting is flat:

```cpp
for (size_t i = 0; i < proofs.size(); ++i)
{
  // ... fetch tx, verify proofs, derive output ...
  total += amount;
  if (kispent_res.spent_status[i])
    spent += amount;
}
```

So the reported reserve scales with how many times the same row appears, not with how many distinct outputs exist on-chain. Stock `get_reserve_proof` only emits each selected transfer once, but nothing stops a custom prover from serializing duplicates; `on_check_reserve_proof` just forwards into `check_reserve_proof`.

## Releases Affected

Re-checked on `master @ 3ad4a5ee8` against the local tree. Issue is in the verifier logic, not a recent regression; any branch with this reserve-proof path has the same gap.

## Steps to Reproduce

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3699522_
