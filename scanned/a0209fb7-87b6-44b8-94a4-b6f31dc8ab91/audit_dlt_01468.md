# [?] askrene: fix use-after-free if remove_htlc_min_violations fails.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-11-13
Source: https://github.com/ElementsProject/lightning/commit/e120202120a60ad82409915e004616f5af9f6cdc
Type: security-commit

## Details
askrene: fix use-after-free if remove_htlc_min_violations fails.

It can only fail on overflow, but if it did, the fail path frees working_ctx
and returns "error_message".

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>
