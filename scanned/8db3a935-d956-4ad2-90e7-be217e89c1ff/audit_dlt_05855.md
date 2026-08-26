# [?] fix: blocks reexecutor panic recovery and shutdown error suppression

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-19
Source: https://github.com/OffchainLabs/nitro/commit/86d7ad1f95aab16be2207921dcc0b22eaf605691
Type: security-commit

## Details
fix: blocks reexecutor panic recovery and shutdown error suppression

- Add handleContextOrFatal to suppress context errors during shutdown
- Wrap AdvanceStateByBlock with recover() to convert panics from
  concurrent trie access races into errors, preventing database
  corruption from abnormal process termination
- Add unit tests for handleContextOrFatal behavior

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
