# [?] fix(pwq): derive `_rate` from request to avoid Guard 1 DoS on rate drop

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2026-05-27
Source: https://github.com/etherfi-protocol/smart-contracts/commit/03d6d5fe1c5741b79e76e3885cea19222310faea
Type: security-commit

## Details
fix(pwq): derive `_rate` from request to avoid Guard 1 DoS on rate drop

Cursor Bugbot finding on commit 6c3f4bf: PWQ claims could DoS when the live
rate drops between fulfill and claim by less than PWQ's 10-wei
`_TOLERANCE_BUFFER`. PWQ admits `amountWithFee` up to `amountForShare + 10`,
but LP's Guard 1 admits only up to `amountCap = floor(shareOfEEth *
amountPerShareCeil / 1e18)`, which is at most ~1 wei above `amountForShare`.
The 1-10 wei window admits at PWQ but reverts at Guard 1 -- claim stuck.

Fix: PWQ now derives `_rate = ceil(amountWithFee * 1e18 / shareOfEEth)`
instead of passing the live rate. By ceiling-rounding, `shareOfEEth *
derivedRate / 1e18 >= amountWithFee`, so `amountCap >= amountWithFee` and
Guard 1 admits the call by construction.

Burn semantics unchanged:
  - Guard 2's max-clamp still picks `shareAtLive` if live dropped below
    the derived rate, ensuring the protocol burns at the honest live cost
  - Guard 3's `shareOfEEth` cap still bounds the burn at the request's
    allocation -- which is the existing PWQ-side expectation

Added regression test in test/LiquidityPool.t.sol:
  test_withdrawGuard1_pwqDerivedRateAdmitsAnyTolerableAmount -- verifies
  that a value within PWQ's tolerance buffer above amountForShare is
  admitted when called with the derived rate.

Suite: 1301 / 1301 unit + invariant tests pass; 97 / 97 PWQ tests pass;
44 / 44 integration tests pass.
