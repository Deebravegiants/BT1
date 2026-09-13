# [H] oneshot has potential Use After Free when used asynchronously

## Summary
Severity: High
Advisory: GHSA-rvr2-r3pv-5m4p
CWE: CWE-362, CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-rvr2-r3pv-5m4p
Type: github-advisory

## Affected
- crates.io: `oneshot` — affected >=0 <0.1.12

## Details
There is a race condition that can lead to a use-after-free if a `oneshot::Receiver` is polled but then dropped instead of polled to completion. This could happen if the receiver future was cancelled while receiving, for example by being wrapped in a timeout future or similar.

When the `Receiver` is polled (`Future::poll`) it writes a waker to the channel and sets it to the `RECEIVING` state. If the `Receiver` was then dropped (instead of polled to completion), the `Drop` implementation on `Receiver` unconditionally swapped the channel state to `DISCONNECTED` and only after doing so it read back its waker from the heap allocation and dropped it. The problem is that the `DISCONNECTED` state could be observed by the `Sender`, which would lead to it deallocating the channel heap memory. If the `Sender` manage to free the channel before the `Receiver` managed to proceed to dropping the waker, then the `Receiver` would read from the freed channel memory (Use After Free).

The fix was submitted in https://github.com/faern/oneshot/pull/74 and published as part of `oneshot` version `0.1.12`.

## References
- https://github.com/faern/oneshot/issues/73
- https://github.com/rustsec/advisory-db/pull/2600
- https://github.com/faern/oneshot/commit/d1a1506010bc48962634807d0dcca682af4f50ba
- https://github.com/faern/oneshot
- https://rustsec.org/advisories/RUSTSEC-2026-0005.html
