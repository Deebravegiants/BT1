# [?] fix(eth-proof-manager): three correctness fixes for validation retries, metrics labels, and verifier panics (#4723)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-07-15
Source: https://github.com/matter-labs/zksync-era/commit/d88daa4540cf6089946ad0411c2f9c544d919054
Type: security-commit

## Details
fix(eth-proof-manager): three correctness fixes for validation retries, metrics labels, and verifier panics (#4723)

Three bug fixes for the `eth_proof_manager` node component.

## Fix 1 — Validation tx retries after first tx was already confirmed

When `send_tx` timed out polling for a receipt, it discarded the
broadcast hash. The retry re-queried the nonce, saw it had advanced
(original tx was mined), and sent a new tx against the next nonce slot —
which reverted on-chain since the validation was already submitted. The
batch stayed `Proven` in the DB and the loop kept retrying until
`validation_tx_attempts` was exhausted.

`send_tx` now returns the broadcast hash alongside any receipt-timeout
error. `send_tx_with_retries` checks all pending hashes for confirmation
before sending a replacement.

## Fix 2 — Truncated addresses in Prometheus labels

`Address` (`H160`) `Display` truncates to `0x<2 bytes>…<2 bytes>`. Both
address label values were set via `.to_string()`, producing e.g.
`0x1a2b…ef01` instead of the full address. Changed to `format!("{:#x}",
addr)`.

## Fix 3 — Verifier and event-handler panics crash the component

`fflonk::verify` can panic on malformed proof data (field elements out
of range). Several `panic!` calls in both event handlers fired on
unexpected ABI token values or unknown `ProvingNetwork` discriminants.
All panics inside the task caused a restart loop instead of marking the
proof invalid.

- `fflonk::verify` wrapped in
`std::panic::catch_unwind(AssertUnwindSafe(...))`.
- `panic!` calls in handlers replaced with `anyhow::bail!`.
- `ProvingNetwork::from_u256` changed to return `anyhow::Result<Self>`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

_Trimmed to 38 lines — full report: https://github.com/matter-labs/zksync-era/commit/d88daa4540cf6089946ad0411c2f9c544d919054_
