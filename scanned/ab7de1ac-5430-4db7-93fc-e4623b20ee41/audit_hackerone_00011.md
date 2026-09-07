# [H] wallet-rpc crash via malformed /gettransactions response (empty txs → vector::front() in check_tx_key / check_tx_proof)

## Summary
Severity: High (CVSS 7.5)
Program: Monero
Weakness: NULL Pointer Dereference
Reporter: bebensap
State: resolved
Disclosed: 2026-08-05T10:23:32.245Z
Source: https://hackerone.com/reports/3693636

## Details
**Repository:** [`monero-project/monero`](https://github.com/monero-project/monero) — `src/wallet/wallet2.cpp` (same response type `COMMAND_RPC_GET_TRANSACTIONS` in `src/rpc/core_rpc_server_commands_defs.h`). Affected branch: `master` (commit `474657ad4`, 2026-04-24).

## Summary

`wallet2` calls the daemon HTTP endpoint `/gettransactions` and treats the answer as trustworthy enough to drive payment verification. The guard only insists that **either** the structured array `txs` **or** the legacy array `txs_as_hex` has length 1:

```cpp
THROW_WALLET_EXCEPTION_IF(!ok || (res.txs.size() != 1 && res.txs_as_hex.size() != 1),
  error::wallet_internal_error, "Failed to get transaction from daemon");
```

If the daemon (or anything on the HTTP path) returns `status: OK`, `txs: []`, and a single blob in `txs_as_hex` whose hash matches the requested txid, the code takes the `else` branch, parses the transaction from hex, runs the crypto checks, then still pulls **pool height and confirmation metadata** from `res.txs.front()` — even though `txs` was empty the whole time. That is undefined behaviour in C++ (`std::vector::front()` on an empty vector). On a normal Release build you usually get an immediate segfault; with ASan you get a clean `vector::front` report.

The same pattern exists in `check_tx_proof` after the identical guard and `if (res.txs.size() == 1) / else` split.

There is a second, narrower footgun on the **cold hardware** `get_tx_key` path: after the same `(txs XOR txs_as_hex)` guard, the code **always** loads the blob from `res.txs_as_hex.front()` (see snippet below) and never branches on `res.txs.size() == 1` first. A response with `txs` populated and `txs_as_hex` empty passes the guard when `txs.size()==1`, but then `txs_as_hex.front()` is the one that blows up. That is a different corner case from the main `check_tx_key` crash, same root cause class: the wallet assumes the two representations stay in sync.

`check_tx_key_helper` (txid overload), current `master`:

```cpp
void wallet2::check_tx_key_helper(const crypto::hash &txid, const crypto::key_derivation &derivation, ...)
{
  ...
  ok = epee::net_utils::invoke_http_json("/gettransactions", req, res, *m_http_client);
  THROW_WALLET_EXCEPTION_IF(!ok || (res.txs.size() != 1 && res.txs_as_hex.size() != 1),
    error::wallet_internal_error, "Failed to get transaction from daemon");

  if (res.txs.size() == 1)
    ok = get_pruned_tx(res.txs.front(), tx, tx_hash);
  else {
    ok = string_tools::parse_hexstr_to_binbuff(res.txs_as_hex.front(), tx_data);
    ...
    tx_hash = cryptonote::get_transaction_hash(tx);
  }
  ...
  check_tx_key_helper(tx, derivation, additional_derivations, address, received);

  in_pool = res.txs.front().in_pool;   // ← txs may still be empty
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3693636_
