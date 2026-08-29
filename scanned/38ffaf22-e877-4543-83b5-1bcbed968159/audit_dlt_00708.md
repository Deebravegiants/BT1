# [?] Improve wallet double-spend detection (#2258)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2022-05-16
Source: https://github.com/ACINQ/eclair/commit/10eb9e932f9c0de06cc8926230d8ad4e2d1d9e2c
Type: security-commit

## Details
Improve wallet double-spend detection (#2258)

Our mechanism to detect double-spending wasn't correctly taking into
account unconfirmed inputs. This was only used in single-funder scenarios
so it could only be an issue in rare edge cases, where it would not lead
to any loss of funds as we keep commit tx data in our DB even for closed
channels.
