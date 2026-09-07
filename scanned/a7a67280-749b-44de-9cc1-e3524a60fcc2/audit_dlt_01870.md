# [?] fix(kona/protocol): add bounds checks in span batch decode to prevent panics on truncated input (#19361)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-10
Source: https://github.com/ethereum-optimism/optimism/commit/37c98925e438efa476c6b598b5113b73dc6dbe76
Type: security-commit

## Details
fix(kona/protocol): add bounds checks in span batch decode to prevent panics on truncated input (#19361)

* fix(kona/protocol): add bounds checks in span batch decode to prevent panics on truncated input

Multiple span batch decode functions panic on truncated input instead of
returning an error. This adds explicit length checks before each unsafe
slice operation:

- prefix.rs: decode_parent_check and decode_l1_origin_check now check
  r.len() >= 20 before split_at(20)
- transactions.rs: decode_tx_sigs now checks r.len() >= 64 before
  indexing r[..32] and r[32..64]
- transactions.rs: decode_tx_tos now checks r.len() >= 20 before
  indexing r[..20]

On short input, each function returns SpanBatchError::Decoding(...)
instead of panicking, allowing the batch to be dropped gracefully —
consistent with Go op-node's io.ReadFull behavior.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* style: fix rustfmt formatting in span batch decode

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* style: fix clippy field_reassign_with_default in span batch tests

Use struct initialization syntax instead of Default::default()
followed by field reassignment.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* style: fix rustfmt formatting for struct initialization

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

---------


_Trimmed to 38 lines — full report: https://github.com/ethereum-optimism/optimism/commit/37c98925e438efa476c6b598b5113b73dc6dbe76_
