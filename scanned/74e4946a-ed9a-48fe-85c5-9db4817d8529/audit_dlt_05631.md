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
asserts `View.Close` does not crash. It fails before this change and
passes after.

Co-authored-by: Sudeep Kumar <sudeep.kumar@erigon.tech>

### db/snapshotsync/snapshots.go
```diff
@@ -1261,6 +1261,13 @@ func (s *RoSnapshots) closeWhatNotInList(l []string) {
 	for segtype, delSegments := range toClose {
 		dirtyFiles := s.dirty[segtype]
 		for _, delSeg := range delSegments {
+			if delSeg.refcount.Load() > 0 {
+				// A live reader (View/RoTx) still holds this segment. Closing it
+				// now would nil its decompressor out from under that reader and
+				// turn the reader's later closeAndRemoveFiles into a crash. Leave
+				// it; it is reaped on a later pass once the reader releases it.
+				continue
+			}
 			delSeg.close()
 			dirtyFiles.Delete(delSeg)
 		}
```

### db/snapshotsync/snapshots_test.go
```diff
@@ -921,3 +921,68 @@ func TestViewPinsGeneration(t *testing.T) {
 	require.Same(oldSrc0, pinned[0].src)
 	require.Same(oldSrc1, pinned[1].src)
 }
+
+// TestCloseWhatNotInListVsLiveViewDoesNotCrash reproduces a use-after-close in
+// the snapshot reopen path. After a merge writes a covering segment, the old
+// sub-segment files remain on disk but TypedSegments -> NoOverlaps drops them
+// from the listing. OpenFolder then hands that list to closeWhatNotInList,
+// which close()s those sub-segments — ignoring that a live View still holds a
+// refcount on them. The View's later Close hits closeAndRemoveFiles on the
+// now-nil decompressor and crashes. This is pure snapshotsync (no merge code),
+// so it fails on main.
+func TestCloseWhatNotInListVsLiveViewDoesNotCrash(t *testing.T) {
+	if testing.Short() {
+		t.Skip()
+	}
+	logger := log.New()
+	dir, require := t.TempDir(), require.New(t)
+
+	verOf := func(i int) snaptype.Version {
+		if i%2 == 1 {
+			return version.V1_1
+		}
+		return version.V1_0
+	}
+
+	// Ten 1k sub-segments per type covering [0, 10000).
+	for from := uint64(0); from < 10_000; from += 1_000 {
+		for i, snT := range snaptype2.BlockSnapshotTypes {
+			createTestSegmentFile(t, from, from+1_000, snT.Enum(), dir, verOf(i), logger)
+		}
+	}
+
+	s := NewRoSnapshots(ethconfig.BlocksFreezing{ChainName: networkname.Mainnet}, dir, snaptype2.BlockSnapshotTypes, true, logger)
+	defer s.Close()
+	require.NoError(s.OpenFolder())
+
+	// A live reader holds the sub-segments (refcount +1), as a merge's View does.
+	v := s.View()
+
+	// Simulate the merge result: a covering [0,10000) segment lands on disk, and
+	// the now-subsumed 1k sub-segments are marked deletable (integrateMergedDirtyFiles).
+	for i, snT := range snaptype2.BlockSnapshotTypes {
+		createTestSegmentFile(t, 0, 10_000, snT.Enum(), dir, verOf(i), logger)
+	}
+	for _, t2 := range s.enums {
+		s.dirty[t2].Walk(func(segs []*DirtySegment) bool {
+			for _, sn := range segs {
+				if sn.To()-sn.From() == 1_000 {
+					sn.canDelete.Store(true)
+				}
+			}
+			return true
+		})
+	}
+
+	// Reopen: NoOverlaps drops the subsumed sub-segments from the list, so
+	// closeWhatNotInList would close them out from under the live View.
+	require.NoError(s.OpenFolder())
+
+	// Closing the View must not crash.
+	defer func() {
+		if r := recover(); r != nil {
+			t.Fatalf("View.Close crashed (use-after-close of a refcount-held segment): %v", r)
+		}
+	}()
+	v.Close()
+}
```
