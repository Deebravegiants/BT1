# [?] fix(node/test): fix sequencer block building race condition (op-rs/kona#2783)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-08-27
Source: https://github.com/ethereum-optimism/optimism/commit/d5d8c5a454bb2ae68e89abe1e6b2d858d006028b
Type: security-commit

## Details
fix(node/test): fix sequencer block building race condition (op-rs/kona#2783)

## Description

We have a race condition in our sequencer block building process:
- When it starts building a block, the sequencer (through the CL node)
sends a `forkchoice_updated` RPC query to the EL
- The L2 EL starts building an empty payload as soon as we query the RPC
endpoint `forkchoice_updated`
- Right after, the CL node sends `get_payload` which seals a payload for
publication

We may have a race condition where the txs from the EL mempool never get
included inside the EL payloads because the blocks get sealed too fast.
