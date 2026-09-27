# [?] Land #26816 gas-underflow fix in main (#26828)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-05-29
Source: https://github.com/MystenLabs/sui/commit/124c64e643a2fea059cb369cc6b96b565fadea7d
Type: security-commit

## Details
Land #26816 gas-underflow fix in main (#26828)

## Summary

Lands the address-balance gas-underflow fix from #26816 into `main`.
#26816 went directly to `releases/sui-v1.72.0` as an out-of-band
emergency fix; this brings it to `main`.

On an `InsufficientFundsForWithdraw` early abort, the gas payment's
address-balance entries are pruned before smashing (real coins are
kept). This avoids underflowing the already-drained address balance at
settlement, which otherwise aborts the settlement transaction.

**This is the unconditional fix only.** The follow-up stacked PR adds
the protocol-version + mainnet accumulator-version gating so the rollout
is safe and mainnet replay stays bit-for-bit correct — kept separate so
that gating diff reads cleanly against this fix.

## Test plan

- [x] `cargo check` / `xclippy` on `sui-adapter-latest`
- [x] e2e regression test `test_gas_smash_no_ab_underflow_on_iffw`
- [ ] CI (incl. simtests)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
