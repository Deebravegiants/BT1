# [?] db/snapshotsync: fix crash due to double close of decompressor  (#21545)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-01
Source: https://github.com/erigontech/erigon/commit/92b22dcf402d01e390e885afa1dcc25f70c802a6
Type: security-commit

## Details
db/snapshotsync: fix crash due to double close of decompressor  (#21545)

## Problem

- `dirtySegment.close()` (closes seg and idx) can happen on subsegments
once some collation does `OpenFolder`, which uses `TypedSegments` which
closes the subsegments.
- `closeWhatNotInList`-- merge calls this and can crash because of close
earlier.
- maybe user in https://github.com/erigontech/erigon/pull/19930 observed
this
- This started happening more after I tried to take snapshot merge off
the build semaphore - https://github.com/erigontech/erigon/pull/21526

```
panic: runtime error: invalid memory address or nil pointer dereference
  seg.(*Decompressor).FilePath
  snapshotsync.(*DirtySegment).closeAndRemoveFiles   snapshots.go:420
  snapshotsync.(*RoTx).Close                         snapshots.go:537
  snapshotsync.(*View).Close
```

## Fix

In `closeWhatNotInList`, skip segments with `refcount > 0`: a live
reader still references them, so closing now would invalidate that
reader. They are reaped on a later pass once the reader releases them
(`closeWhatNotInList` already runs on every `OpenFolder`).

`View`/`BeginRo` stays lock-free (#20490) — the fix is purely in the
close path.

## Test

`TestCloseWhatNotInListVsLiveViewDoesNotCrash` reproduces the crash
deterministically (pure `snapshotsync`, no merge machinery): it builds
sub-segments, opens a `View` over them, drops a covering merged file on
disk, reopens (so `NoOverlaps` removes the subs from the list), and

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/92b22dcf402d01e390e885afa1dcc25f70c802a6_
