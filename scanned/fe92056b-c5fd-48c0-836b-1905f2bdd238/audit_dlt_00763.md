# [?] fix(abci): prevent panic on unlock in socket server panic recovery (#5593)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-04-24
Source: https://github.com/cometbft/cometbft/commit/320e79ef982a69a5e32ec98a49ef6b6db1ad9c4f
Type: security-commit

## Details
fix(abci): prevent panic on unlock in socket server panic recovery (#5593)

---

#### PR checklist
Fix a bug in handleRequests where the panic recovery defer function
would attempt to unlock appMtx even when the lock was never acquired.
- [x] Tests written/updated
- [x] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

---------

Co-authored-by: Alex | Cosmos Labs <alex@cosmoslabs.io>
Co-authored-by: Dmitry S <11892559+swift1337@users.noreply.github.com>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>
