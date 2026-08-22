# [?] p2p/tracker: fix crash in clean when tracker is stopped

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2026-08-02
Source: https://github.com/etclabscore/core-geth/commit/ff7d98f1abeb010e6b9f577e7a52c1f5cab71b5b
Type: security-commit

## Details
p2p/tracker: fix crash in clean when tracker is stopped

Port of go-ethereum#33940 (upstream 9962e2c9f). The clean method is
scheduled via time.AfterFunc and may fire after Stop has set t.expire
to nil, crashing on the nil list. Bail out of clean when the tracker
has been stopped.

(cherry picked from commit 9962e2c9f33a666d634a0d3cb90478b608cf8b46)
Co-authored-by: Felix Lange <fjl@twurst.com>
Co-authored-by: Claude Fable 5 <noreply@anthropic.com>
