# [?] fix(kona): return error instead of panic on unknown batch type (#20000)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-04-10
Source: https://github.com/ethereum-optimism/optimism/commit/88cd69c83a01986e98508b4ab9415e45de7415fa
Type: security-commit

## Details
fix(kona): return error instead of panic on unknown batch type (#20000)

* fix(kona): return error instead of panic on unknown batch type

BatchType::from(u8) panicked on unknown batch type values. This is a
protocol deviation — the OP spec requires unknown batch versions to be
treated as invalid and ignored, matching op-node's behavior of returning
an error and skipping to the next channel.

Replace From<u8> with TryFrom<u8>, add UnknownBatchType variant to
BatchDecodingError, and propagate the error in Batch::decode.

Fixes ethereum-optimism/optimism-private#484

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(kona): rustfmt

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
