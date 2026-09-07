# [?] lightningd: fix crash in channel_control.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-10-22
Source: https://github.com/ElementsProject/lightning/commit/5a530e6c46974f86b4864903e668958ae8f412f5
Type: security-commit

## Details
lightningd: fix crash in channel_control.

I got a NULL deref on `infcopy->remote_funding = *inflight->funding->splice_remote_funding`
at once point in testing, so this should prevent that from happening,
yet still allow us to catch it in CI if it happens again.

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>
