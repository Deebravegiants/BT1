# [?] Prevent overlapping sync work panic (#1736)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2023-07-20
Source: https://github.com/ava-labs/avalanchego/commit/b0fdf4273f190cbd702f8afbf2258483f4570fe0
Type: security-commit

## Details
Prevent overlapping sync work panic (#1736)

## Patch
### x/sync/manager.go
```diff
@@ -641,6 +641,16 @@ func (m *Manager) enqueueWork(work *workItem) {
 	// Find the middle point.
 	mid := midPoint(work.start, work.end)
 
+	if bytes.Equal(work.start, mid) || bytes.Equal(mid, work.end) {
+		// The range is too small to split.
+		// If we didn't have this check we would add work items
+		// [start, start] and [start, end]. Since start <= end, this would
+		// violate the invariant of [m.unprocessedWork] and [m.processedWork]
+		// that there are no overlapping ranges.
+		m.unprocessedWork.Insert(work)
+		return
+	}
+
 	// first item gets higher priority than the second to encourage finished ranges to grow
 	// rather than start a new range that is not contiguous with existing completed ranges
 	first := newWorkItem(work.localRootID, work.start, mid, medPriority)
```
