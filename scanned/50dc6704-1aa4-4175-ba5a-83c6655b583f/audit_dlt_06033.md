# [?] fix(consensus-adapter): actually insert `EndOfPublish` (if absent) for re-submission on crash recovery (#10578)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-03-04
Source: https://github.com/iotaledger/iota/commit/41729efe0580c5cf41f13844a737813f5faf7a00
Type: security-commit

## Details
fix(consensus-adapter): actually insert `EndOfPublish` (if absent) for re-submission on crash recovery (#10578)

# Description of change

This PR fixes a plain inversion bug in `submit_recovered` of
`ConsensusAdapter`. Specifically, if the list of `recovered` pending
consensus transactions does not contain an `EndOfPublish` transaction,
the condition
`recovered.iter().any(ConsensusTransaction::is_end_of_publish)` is
`false`, which means `EndOfPublish` will never be resubmitted in the
case of crash recovery, likely leading to epoch transitioning getting
stuck. In contrast, if `EndOfPublish` is already present in recovered,
the current code on `develop` needlessly inserts another `EndOfPublish`.
However, in the actual crash-recovery scenario, we would like to insert
`EndOfPublish` into `recovered` if it was absent; hence, the inverted
condition
`!recovered.iter().any(ConsensusTransaction::is_end_of_publish)` is
correct.

Other minor changes include improving the corresponding comments and
removing `#[expect(clippy::collapsible_if)]` as it is no longer needed.

> [!NOTE]
> 1. The bug was discovered during the certificate-less epoch change PoC
([branch](https://github.com/iotaledger/iota/tree/protocol-research/feat/certificate-less-epoch-boundary-coordination)).
> 2. Upstream added this fix as a part of
https://github.com/MystenLabs/sui/pull/23122.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes


_Trimmed to 38 lines — full report: https://github.com/iotaledger/iota/commit/41729efe0580c5cf41f13844a737813f5faf7a00_
