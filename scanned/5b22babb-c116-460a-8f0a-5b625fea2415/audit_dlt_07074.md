# [?] cl/utils: fix data race in ParallelExecutor.Execute (#18073)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-11-28
Source: https://github.com/erigontech/erigon/commit/fec2a5fa36e1e43d3b194691b059415b4ea16415
Type: security-commit

## Details
cl/utils: fix data race in ParallelExecutor.Execute (#18073)

Changed eliminates a data race in ParallelExecutor.Execute where
multiple goroutines were writing to a shared error variable without
synchronization, leading to nondeterministic last-writer-wins behavior
and potential race detector reports. The fix introduces a sync.Once to
record only the first non-nil error returned by any worker, which aligns
with the repository’s prevalent errgroup-style “first error wins”
semantics while preserving the existing API and behavior for call sites
that intentionally ignore Execute’s return value. This approach avoids
heavier synchronization or API changes, keeps overhead minimal, and
makes error handling deterministic and race-free.

## Patch
### cl/utils/threading/parallel_executor.go
```diff
@@ -21,6 +21,7 @@ func NewParallelExecutor() *ParallelExecutor {
 // close work channel and finish
 func (wp *ParallelExecutor) Execute() error {
 	var errOut error
+	var once sync.Once
 	if dbg.CaplinSyncedDataMangerDeadlockDetection {
 		st := dbg.Stack()
 		ch := make(chan struct{})
@@ -38,7 +39,7 @@ func (wp *ParallelExecutor) Execute() error {
 		go func(job func() error) {
 			defer wp.wg.Done()
 			if err := job(); err != nil {
-				errOut = err
+				once.Do(func() { errOut = err })
 			}
 		}(job)
 	}
```
