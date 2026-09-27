# [?] Fix underflow in blinded path amt_to_forward

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-06-15
Source: https://github.com/lightningdevkit/rust-lightning/commit/e560ec170682d36e363361c6e8f09c958edd237b
Type: security-commit

## Details
Fix underflow in blinded path amt_to_forward

If we have a high (200%+) proportional fee as an intermediate blinded node
combined with a low inbound amount, we previously had some code that calculated
the outbound amount of the forward that would've underflowed. This would've
caused a panic in debug builds and caused us to relay a payment that should've
been rejected (due to being unable to cover our high fee) in release builds.

Reported by Project Loupe.
