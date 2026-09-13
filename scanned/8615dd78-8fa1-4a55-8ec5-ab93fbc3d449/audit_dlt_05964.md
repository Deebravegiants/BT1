# [?] qt: Fix potential crash due to mis-use of showProgress

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2023-03-29
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/93805bae3ba896216e7acfbe13c10dc2bb1c9dac
Type: security-commit

## Details
qt: Fix potential crash due to mis-use of showProgress

Summary
---

This fixes #485.  I traced the issue to the face that `100` was being
sent twice when importing a wallet.  The first time, the progress dialog
is deleted, but the pointer is never set to nullptr.  The second time,
the dangling pointer refers to deleted memory, and UB happens.

This commit fixes this by just enforcing invariants more strictly and
"doing the right thing".

When testing with this MR, I added extra debug prints to verify this was
the issue and this is what I got, verifying that the app no longer
crashes and invariants are respected:

    2023-03-29T12:10:28Z [default wallet] Rescan started from block 0000000066ff29c5752e769ee1a60627eebd40f36d55576c7a83b8e5505daaa6...
    2023-03-29T12:10:28Z !! shotProgress: 100, p = 0x0
    2023-03-29T12:10:28Z !! shotProgress: 100, p = 0x0

Test Plan
---

- `ninja check-all`
- Attempt to reproduce #485 both with and without this fix, and observe
  that this fix works and doesn't lead to an app crash.
