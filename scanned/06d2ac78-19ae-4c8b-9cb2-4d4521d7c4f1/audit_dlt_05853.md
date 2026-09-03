# [?] Harden blocks reexecutor with panic recovery for trie-cache eviction races

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-22
Source: https://github.com/OffchainLabs/nitro/commit/757ba93e5641897b4b3fa3a02782678a1ae88914
Type: security-commit

## Details
Harden blocks reexecutor with panic recovery for trie-cache eviction races

- Wrap AdvanceStateByBlock in recover() to convert panics from
  concurrent trie-cache eviction races into errors, preventing
  abnormal process termination
- Add unit tests for reportFatalErr (basic, channel-full, multiple
  error types) and panic recovery in advanceStateUpToBlock

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
