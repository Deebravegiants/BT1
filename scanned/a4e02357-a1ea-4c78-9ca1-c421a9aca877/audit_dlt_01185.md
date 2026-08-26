# [?] fix: prevent EVM memory size overflow crash for extreme memory requests (#9887)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2025-12-05
Source: https://github.com/NethermindEth/nethermind/commit/c43523691f158c7af7a6bfc4446230202497dc94
Type: security-commit

## Details
fix: prevent EVM memory size overflow crash for extreme memory requests (#9887)

fix: prevent EVM memory size overflow crash for large memory requests

The memory validation in CheckMemoryAccessViolation was checking against
long.MaxValue, but .NET arrays are limited to int.MaxValue. When memory
requests exceeded int.MaxValue but were less than long.MaxValue, the
word-aligned size calculation would overflow when cast to int, causing
ArrayPool.Rent() to allocate an incorrectly sized array and subsequent
Array.Copy operations to crash.

This fix changes the limit from long.MaxValue to (int.MaxValue - WordSize + 1)
to ensure that after word alignment, the resulting size still fits in int.

Root cause:
- Memory size validation checked: totalSize > long.MaxValue
- But .NET arrays require: (int)Size to be valid
- Word alignment adds up to 31 bytes: Size = totalSize + (32 - totalSize % 32)
- When totalSize > int.MaxValue - 31, (int)Size overflows

Example crash scenario:
1. Contract requests 4GB (0xffffffff) memory via DELEGATECALL
2. Validation passes (4GB < long.MaxValue)
3. Word-aligned Size = 0x100000000 (exceeds int.MaxValue)
4. (int)Size = 0 (overflow)
5. ArrayPool.Rent(0) returns tiny array
6. Array.Copy crashes with "Destination array was not long enough"

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude <noreply@anthropic.com>
