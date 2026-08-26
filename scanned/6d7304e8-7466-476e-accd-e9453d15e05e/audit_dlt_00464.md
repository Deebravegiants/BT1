# [?] Fix overflow error handling in ConservationOfLumens

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2025-12-19
Source: https://github.com/stellar/stellar-core/commit/3647e1e1bd8975e142e8e7dadc24fd6f6767cd4d
Type: security-commit

## Details
Fix overflow error handling in ConservationOfLumens

Previously, processEntryIfNew would log overflow errors but allow the
invariant to continue, causing it to pass despite data corruption. Now
passes error string by reference and returns it from the invariant,
causing proper failure on overflow.

Changes:
- Add errorMsg parameter to processEntryIfNew
- Remove CLOG_ERROR calls, use fmt::format to set errorMsg
- Update scanLiveBucket and scanHotArchiveBucket to accept and pass errorMsg
- Check errorMsg after scan phases and return immediately if set

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
