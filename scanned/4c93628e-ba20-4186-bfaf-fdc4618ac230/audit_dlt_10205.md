# [?] go/common/workerpool: Fix pool shutdown race condition

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2020-10-16
Source: https://github.com/oasisprotocol/oasis-core/commit/c4ff6cbd91a86d21c35bf65ad3f622189a1a9511
Type: security-commit

## Details
go/common/workerpool: Fix pool shutdown race condition

## Patch
### go/common/workerpool/workerpool.go
```diff
@@ -89,6 +89,13 @@ func (p *Pool) Quit() <-chan struct{} {
 // Submit adds a task to the pool's queue and returns a channel that will be closed
 // once the task is complete.
 func (p *Pool) Submit(job func()) <-chan struct{} {
+	p.lock.Lock()
+	defer p.lock.Unlock()
+
+	if p.currentCount == 0 {
+		return nil
+	}
+
 	desc := &jobDescriptor{
 		job:        job,
 		completeCh: make(chan struct{}),
```
