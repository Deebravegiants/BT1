# [?] chore(deps): update h2 to 0.4.17 to fix RUSTSEC-2026-0258 (#12704)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-08-20
Source: https://github.com/iotaledger/iota/commit/47734c9f2a3ad876d69550071824452346964575
Type: security-commit

## Details
chore(deps): update h2 to 0.4.17 to fix RUSTSEC-2026-0258 (#12704)

# Description of change

- Updates `h2` from 0.4.12 to 0.4.17 in `Cargo.lock` to resolve
[RUSTSEC-2026-0258](https://rustsec.org/advisories/RUSTSEC-2026-0258)
(h2 unbounded empty DATA frames).
- Fixes the failing nightly `cargo deny check advisories` job:
https://github.com/iotaledger/iota/actions/runs/32191017965/job/95885133803
- Also carries a few incidental transitive lockfile adjustments from
`cargo update -p h2` (`spin`, `socket2`, `windows-sys`).

## Links to any relevant issues

None.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [x] Patch-specific tests (correctness, functionality coverage): `cargo
deny check advisories` passes locally.
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [x] I have checked that new and existing unit tests pass locally with
my changes

<!-- Do not remove: everything below this line is ignored by the
release-notes check. -->

---

---------

Co-authored-by: Claude Fable 5 <noreply@anthropic.com>
