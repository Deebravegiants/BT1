# [M] wallet-rpc describe_transfer uses real_output_in_tx_index instead of real_output: cold-wallet pre-sign review shows wrong ring member

## Summary
Severity: Medium (CVSS 5.4)
Program: Monero
Weakness: Array Index Underflow
Reporter: bebensap
State: resolved
Disclosed: 2026-08-05T10:23:08.581Z
Source: https://hackerone.com/reports/3723315

## Details
# `describe_transfer` wallet-rpc indexes the ring with `real_output_in_tx_index` instead of `real_output` → cold-wallet pre-sign review shows a decoy as the "real input"

**Repository:** [`monero-project/monero`](https://github.com/monero-project/monero) — `src/wallet/wallet_rpc_server.cpp`. Reproduced against unmodified upstream source built from `/home/beni/Monero/monero-src` (HEAD `082b600a2`, master). The same two lines exist on `release-v0.18`.

## Summary

`describe_transfer` is the JSON-RPC method a cold-wallet operator (or a GUI / payment integration wrapping `monero-wallet-rpc`) calls before signing an unsigned or multisig txset, to see what the transaction is actually going to do. For each input it returns a `sources[i]` block that includes `global_index` and `pubkey` — advertised as the real ring entry being spent.

The handler reads those two fields from the wrong slot of the ring. `tx_source_entry` carries two distinct numbers: `real_output` (the position of the real entry inside `outputs`, the ring) and `real_output_in_tx_index` (the position the output had inside its source transaction's `vout`). They are not the same. `outputs` is the ring (size = ring_size, currently 16); `real_output_in_tx_index` is bounded only by the source tx's vout length and is `0` for any coinbase-derived UTXO. `on_describe_transfer` indexes the ring with the second number, so the global_index and pubkey it shows the operator describe whichever ring slot happens to sit at position `real_output_in_tx_index` — usually a decoy.

The signing path is unaffected. `construct_tx_with_tx_key` reads the real entry from `outputs[real_output]` (`cryptonote_tx_utils.cpp:365,373`); so do `multisig_tx_builder_ringct.cpp:113` and `simplewallet.cpp:6213`. Only this RPC mixes them up. The result is that `describe_transfer` and the broadcast tx disagree about which output the wallet is about to spend.

Buggy block, `src/wallet/wallet_rpc_server.cpp` (master `082b600a2`):

```cpp
1564  for (size_t s = 0; s < cd.sources.size(); ++s)
1565  {
1566    const cryptonote::tx_source_entry &src_in = cd.sources[s];
1567    wallet_rpc::COMMAND_RPC_DESCRIBE_TRANSFER::source &src_out = desc.sources.emplace_back();
1568    src_out.amount = src_in.amount;
1569    src_out.global_index = src_in.outputs.at(src_in.real_output_in_tx_index).first;
1570    src_out.rct = src_in.rct;
1571    src_out.pubkey = epee::string_tools::pod_to_hex(
1572                        src_in.outputs.at(src_in.real_output_in_tx_index).second);
```

The struct definition documents the meaning, and the serialiser only bounds `real_output`, not `real_output_in_tx_index`:

```cpp
// src/cryptonote_core/cryptonote_tx_utils.h
45  std::vector<output_entry> outputs;     // index + key + ringct commitment (the RING)
46  uint64_t real_output;                  // index in `outputs` of the real entry
49  uint64_t real_output_in_tx_index;      // index in the SOURCE TX's vout
...
68    if (real_output >= outputs.size())   // serialiser only enforces this one
69      return false;
```


_Trimmed to 38 lines — full report: https://hackerone.com/reports/3723315_
