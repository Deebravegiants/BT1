# [?] fix(mempool): panic when the app returns error on CheckTx request (#2894)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-04-26
Source: https://github.com/cometbft/cometbft/commit/98983fc64308843e07282f82b72e6b82fff7a573
Type: security-commit

## Details
fix(mempool): panic when the app returns error on CheckTx request (#2894)

Closes #2225

If the app returns an error on an ABCI call (in particular CheckTx),
CometBFT should stop, because the error is unrecoverable.

---

#### PR checklist

- [X] Tests written/updated
- [X] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [X] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec
