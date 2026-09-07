# [?] [mfp] Enable DoS protection for MFP submitted user tx (#23334)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-09-11
Source: https://github.com/MystenLabs/sui/commit/606de5ea650f7f02a265b98329c48f5935c35725
Type: security-commit

## Details
[mfp] Enable DoS protection for MFP submitted user tx (#23334)

## Description 

Implements a submitted transaction cache to prevent DoS attacks through
excessive transaction resubmissions. The cache tracks all transactions
submitted to consensus and applies spam weights to clients that exceed
submission limits, integrating with the existing traffic controller for
throttling.

Submitted Transaction Cache (submitted_transaction_cache.rs)
- Tracks all transactions submitted through mfp
- Gas-price-based amplification factor allowing higher gas transactions
more resubmissions
- Allow for additional retry tolerance on top of amplification factor
- Round-based garbage collection following existing consensus cache
patterns
- Tracks submitter client IP for traffic attribution

Traffic Controller Integration
- ConsensusHandler increments submission count when seeing transactions
in consensus output
- Calculates spam weight using a simple Weight::one() for all excess
transaction resubmissions
- Applies spam weight to the original submitter's IP address via traffic
controller tally

## Test plan 

pending ptn tests

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.


_Trimmed to 38 lines — full report: https://github.com/MystenLabs/sui/commit/606de5ea650f7f02a265b98329c48f5935c35725_
