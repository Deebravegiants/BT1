# [?] Avoid deadlock by nonblocking session end from poh (#5651)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2025-04-07
Source: https://github.com/anza-xyz/agave/commit/41b445e907fa802d012304fba394d25faa26af20
Type: security-commit

## Details
Avoid deadlock by nonblocking session end from poh (#5651)

## Patch
### unified-scheduler-pool/src/lib.rs
```diff
@@ -2008,6 +2008,10 @@ impl<S: SpawnableScheduler<TH>, TH: TaskHandler> ThreadManager<S, TH> {
     }
 
     fn end_session(&mut self) {
+        self.do_end_session(false)
+    }
+
+    fn do_end_session(&mut self, nonblocking: bool) {
         if self.are_threads_joined() {
             assert!(self.session_result_with_timings.is_some());
             debug!("end_session(): skipping; already joined the aborted threads..");
@@ -2026,6 +2030,17 @@ impl<S: SpawnableScheduler<TH>, TH: TaskHandler> ThreadManager<S, TH> {
             .send(NewTaskPayload::CloseSubchannel)
             .is_err();
 
+        // In addition to the later session result receiving, also skip thread joining, which is
+        // part of necessary bookkeeping on scheduler abortion, even if detected; Otherwise, we
+        // could be dead-locked around poh, because we would technically wait on handler thread
+        // before joining in _the poh thread_. Nonblocking session ending is guaranteed to be
+        // followed by blocking session ending in the replay stage thread. The first nonblocking
+        // session ending is special-cased only for block production poh. The second real session
+        // ending will properly take care of all the skipped clean up.
+        if nonblocking {
+            return;
+        }
+
         if abort_detected {
             self.ensure_join_threads_after_abort(true);
             return;
@@ -2159,7 +2174,19 @@ impl<TH: TaskHandler> InstalledScheduler for PooledScheduler<TH> {
     }
 
     fn pause_for_recent_blockhash(&mut self) {
-        self.inner.thread_manager.end_session();
+        // This fn is called from poh thread for block production, while poh lock is held. So, we
+        // can't wait for session ending here to avoid deadlock with handler threads, which also
+        // try to lock the poh to commit transactions. Actually, just nonblocking signaling is
+        // enough for block production unlike block verification.
+        //
+        // That's because the unified scheduler is the ultimate consumer of session ending signal
+        // in block production, while a certain external system (= the replay stage) is the
+        // ultimate consumer of session ending signal in block verification. In the later case, the
+        // semantics of session ending should be defined from the external system's perspective;
+        // i.e. the completion of all scheduled task inside the unified scheduler. So, it can't be
+        // nonblocking there.
+        let nonblocking = matches!(self.context().mode(), BlockProduction);
+        self.inner.thread_manager.do_end_session(nonblocking);
     }
 }
 
```
