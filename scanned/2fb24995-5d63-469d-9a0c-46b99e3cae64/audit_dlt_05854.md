# [?] fix: prevent deadlock and nil panic in blocks reexecutor

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-19
Source: https://github.com/OffchainLabs/nitro/commit/49919fceb7051449c12ed2c45a114151b40063fc
Type: security-commit

## Details
fix: prevent deadlock and nil panic in blocks reexecutor

Add done-channel signals on early-return error paths in
LaunchBlocksReExecution so that Impl's done-counting loop does not
deadlock. Move GetHeaderByNumber(currentBlock) outside the goroutine
to catch nil before passing it to advanceStateUpToBlock, and properly
release state on that error path. Also fix requestValidity timeout in
data streaming protocol test.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
