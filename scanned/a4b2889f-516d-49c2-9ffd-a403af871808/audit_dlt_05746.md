# [?] ledger: fix panic with async verify and dropping ConfirmationProgress (#11234)

## Summary
Severity: Unknown
Chain: Solana
Component: jito-foundation/jito-solana
Published: 2026-03-12
Source: https://github.com/jito-foundation/jito-solana/commit/1997085ea158eb1f9bc3ac2162d0a6bd3d8869ef
Type: security-commit

## Details
ledger: fix panic with async verify and dropping ConfirmationProgress (#11234)

If ConfirmationProgress gets dropped while async verifications are still
in flight, AsyncVerificationProgress::spawn panics trying to send back
resuts to a now disconnected channel.

The fix is to remove expect() and ignore results instead.
