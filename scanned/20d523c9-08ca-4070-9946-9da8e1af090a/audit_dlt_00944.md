# [?] fix: Buffer overflow in home-screen plugin tagline formatting

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-05-11
Source: https://github.com/LedgerHQ/app-ethereum/commit/1191ba202dcef992614f68eb73c3d9080ec1ede5
Type: security-commit

## Details
fix: Buffer overflow in home-screen plugin tagline formatting

The home-screen plugin tagline builder accumulated the FORMAT_PLUGIN
template length and the caller-controlled caller_app->name length into
a uint8_t. A sufficiently long caller name could wrap that accumulator,
leading to an undersized allocation for g_tag_line and a subsequent
snprintf overflow into adjacent memory across the on-device library-call
trust boundary.

Bound the plugin name with strnlen() against an explicit maximum and
perform the length math in size_t to make the wrap unreachable.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
