# [?] Fix race condition in ChunkEndorsementTracker (#11452)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-06-04
Source: https://github.com/near/nearcore/commit/041c32c760d335bbb7c70ab881a741bb7acaaccb
Type: security-commit

## Details
Fix race condition in ChunkEndorsementTracker (#11452)

Fixes: https://github.com/near/nearcore/issues/11445

In the new version all operations are done by
`ChunkEndorsementTrackerInner` which has `&mut self` on all methods,
which prevents most races. Apart from that when adding a pending
endorsement we check whether the header for this chunk has already been
seen and if so we treat this endorsement as non-pending.
