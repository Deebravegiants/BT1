# [?] feat(dev-tools, iota-core): add double-spend safety log-audit tool for p-cool (#11987)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-06-24
Source: https://github.com/iotaledger/iota/commit/5082be69fdb5e7a2b64e4cae6da228d7d7e485d3
Type: security-commit

## Details
feat(dev-tools, iota-core): add double-spend safety log-audit tool for p-cool (#11987)

# Description of change

Adds `dev-tools/iota-private-network/scripts/log-audit/`, a tool that
reconciles validator/fullnode/stress logs from a double-spend stress run
to prove no double-spend is leaked under the white-flag (P-COOL) flow.
- in `iota-core` additional logging was added in post-consensus
validation.
## Links to any relevant issues

fixes #11602.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [x] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes
