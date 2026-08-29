# [?] Fix a race condition with TrustedPublisherServer:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2020-07-25
Source: https://github.com/XRPLF/rippled/commit/d317060ae455dd31251bfe5d7d391c9c72420cd3
Type: security-commit

## Details
Fix a race condition with TrustedPublisherServer:

There was a race condition in `on_accept` where the object's destructor
could run while `on_accept` was called.

This patch ensures that if `on_accept` is called then the object remains
valid for the duration of the call.
