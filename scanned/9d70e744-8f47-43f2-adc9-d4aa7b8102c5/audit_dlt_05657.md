# [?] Fix data race on s.head.full in postPayloadTasks (#16839)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-05-27
Source: https://github.com/OffchainLabs/prysm/commit/5b44483086f0331c1d5647cba196947ba493607a
Type: security-commit

## Details
Fix data race on s.head.full in postPayloadTasks (#16839)

- `s.head.full = true` written with no lock — races with `setHead` and
RLock readers
- Take `headLock.Lock()` and re-check `s.head.root == root` before
mutating
