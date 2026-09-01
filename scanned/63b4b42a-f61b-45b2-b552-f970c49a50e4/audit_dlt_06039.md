# [?] fix: harden deserialization and message handlers against panics (#4844)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2026-06-03
Source: https://github.com/iotexproject/iotex-core/commit/83768641751bec0c72bab14d9c2af30299a9b6e2
Type: security-commit

## Details
fix: harden deserialization and message handlers against panics (#4844)

* fix: harden deserialization and message handlers against panics

Replace five panic-prone paths reachable from peer-controlled or untrusted
input with explicit error returns / safe fallbacks:

- action.envelope.LoadProto: return ErrInvalidAct on unknown TxType instead
  of panicking on TxType >= 5.
- evm.ExtractRevertMessage: bound-check the Error(string) ABI payload and
  reject non-UTF-8 messages; fall back to hex on malformed input.
- evm.StateDBAdapter.AddLog: guard the in-contract-transfer topic check
  against empty topics.
- chainservice.Filter / ReportFullness: reject blocks with nil Header or
  nil Header.Core before dereferencing Height.
- endorsement.Endorsement.LoadProto: return an error on nil proto instead
  of panicking before signature/delegate verification.

Add unit tests covering each new error path.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* fix: address three HIGH-severity peer-reachable attack vectors

Findings #6, #7, #9 from the security audit, all read-verified:

#6 nodeinfo: HandleNodeInfo dereferenced msg.Info without a nil check, so
any peer could crash a node by broadcasting NODE_INFO with Info=nil.
Now guarded; non-panic test added.

#7 actsync: RequestActionsFromNeighbors had no upper bound on the number
of in-flight requests, letting a peer drown a node in outbound traffic.
Cap added; tests cover cap respected under flood, dedup must not
double-count, concurrent flood respects cap.

#9 server/itx: admin mux (/pause, /unpause, /producer-keys, pprof) was
bound to 0.0.0.0, letting any peer that could reach the admin port halt
block production with an unauthenticated POST to /pause. Now bound to

_Trimmed to 38 lines — full report: https://github.com/iotexproject/iotex-core/commit/83768641751bec0c72bab14d9c2af30299a9b6e2_
