# [?] Fix HTLC fulfill race condition in integration spec (#1666)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2021-01-19
Source: https://github.com/ACINQ/eclair/commit/9c4ab7d923a8e6947689c0129a2bfc6169aff657
Type: security-commit

## Details
Fix HTLC fulfill race condition in integration spec (#1666)

We were extracting F's commit tx from its internal state right after receiving
the `PaymentSent` event. The issue is that this could happen before the fulfill
was completely signed on both sides, so the commit tx we obtained would still
contain the HTLC and would be different from the one F would publish when
closing.
