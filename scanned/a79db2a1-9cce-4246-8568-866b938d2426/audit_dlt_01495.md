# [?] Fixed race condition on payment handler init (#1208)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2019-11-13
Source: https://github.com/ACINQ/eclair/commit/e5060d9377e4e722ce517d6b573f3dd0c0121876
Type: security-commit

## Details
Fixed race condition on payment handler init (#1208)

When an actor sends a message to itself as part of its class definition,
there is no guarantee that this message will be processed first. Relying
on that to set the default payment handler is problematic and causes
race conditions in tests.
