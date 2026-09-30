# [?] fix(runner): don't panic when the executor child dies during input-send (#2834)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2026-06-08
Source: https://github.com/succinctlabs/sp1/commit/7bcfcdc8b424d81adfa8d6509198d05a32c8f2ae
Type: security-commit

## Details
fix(runner): don't panic when the executor child dies during input-send (#2834)

Co-authored-by: Tamir Hemo <tamir@succinct.xyz>

## Patch
### crates/core/executor/src/errors.rs
```diff
@@ -73,6 +73,13 @@ pub enum ExecutionError {
     #[error("SP1 program consumes too much memory")]
     TooMuchMemory(),
 
+    /// The child executor process was killed by an external signal (e.g. the OS / cgroup
+    /// OOM-killer), not by exceeding its own memory budget. Kept distinct from
+    /// [`ExecutionError::TooMuchMemory`] (the program's fault) so host-pressure kills aren't
+    /// mislabelled as the program's own.
+    #[error("child executor process was killed externally")]
+    ChildKilled(),
+
     /// A generic error.
     #[error("{0}")]
     Other(String),
```

### crates/core/runner/src/native.rs
```diff
@@ -16,7 +16,10 @@ use std::{
     os::unix::process::ExitStatusExt,
     process::{Child, Command, Stdio},
     ptr::NonNull,
-    sync::Arc,
+    sync::{
+        atomic::{AtomicBool, Ordering},
+        Arc,
+    },
     thread::{self, JoinHandle},
     time::Duration,
 };
@@ -32,7 +35,9 @@ pub struct MinimalExecutorRunner {
     memory: SharedMemory,
     consumer: Option<ShmTraceRing>,
 
-    process: Option<(Child, JoinHandle<()>)>,
+    // The flag is set by the memory monitor when it SIGKILLs the child for exceeding its RSS
+    // budget, so that kill can be told apart from an external (OOM-killer) one.
+    process: Option<(Child, JoinHandle<()>, Arc<AtomicBool>)>,
     output: Option<Result<Output, ExecutionError>>,
 
     global_clk: u64,
@@ -129,30 +134,50 @@ impl MinimalExecutorRunner {
 
         if self.process.is_none() {
             // Start the process
-            let mut child = spawn_restricted(
+            let (mut child, killed_by_monitor) = spawn_restricted(
                 Command::new(crate::binary::get_binary_path()),
                 self.input.memory_limit,
             )
             .map_err(|e| ExecutionError::Other(format!("failed to spawn child process: {e}")))?;
 
-            {
-                let stdin = child.stdin.take().expect("open stdin");
-                let mut writer = BufWriter::new(stdin);
-                bincode::serialize_into(&mut writer, &self.input).expect("sending input");
-                writer.flush().expect("flushing input");
-            }
-
+            // Start draining stderr before sending input. The input write is blocking, so a
+            // child that fills its stderr pipe first would deadlock the exchange; draining
+            // from the start also preserves its diagnostics if it dies before reading input.
             let stderr = child.stderr.take().expect("open stderr");
             let id = self.input.id.clone();
             let log_handle = thread::spawn(move || {
                 let reader = BufReader::new(stderr);
-                use BufRead;
                 for l in reader.lines().map_while(Result::ok) {
                     tracing::debug!("CHILD {}: {}", id, l);
                 }
             });
 
-            self.process = Some((child, log_handle));
+            // Send the program input. If the child died during startup (e.g. OOM-killed) the
+            // pipe breaks; surface its exit cause instead of panicking on the write.
+            let send_result = {
+                let stdin = child.stdin.take().expect("open stdin");
+                let mut writer = BufWriter::new(stdin);
+                match bincode::serialize_into(&mut writer, &self.input) {
+                    Ok(()) => writer.flush().map_err(|e| e.to_string()),
+                    Err(e) => Err(e.to_string()),
+                }
+            };
+            if let Err(send_err) = send_result {
+                // The write almost always fails because the child already died. Kill defensively
+                // in case it didn't, so the reap can't block; then collect its exit status and logs.
+                let _ = child.kill();
+                let status = child.wait().expect("wait for child to exit");
+                let _ = log_handle.join();
+                let error = if status.success() {
+                    ExecutionError::Other(format!("failed sending input to child: {send_err}"))
+                } else {
+                    child_exit_error(&status, &killed_by_monitor)
+                };
+                self.output = Some(Err(error.clone()));
+                return Err(error);
+            }
+
+            self.process = Some((child, log_handle, killed_by_monitor));
         }
 
         if let Some(consumer) = &self.consumer {
@@ -172,12 +197,8 @@ impl MinimalExecutorRunner {
                     }
                     TraceResult::Crashed(details) => {
                         // Process logs, they might provide insight into why the program crashed.
-                        self.process
-                            .take()
-                            .unwrap()
-                            .1
-                            .join()
-                            .expect("wait for log thread to finish");
+                        let (_, log_thread, _) = self.process.take().unwrap();
+                        log_thread.join().expect("wait for log thread to finish");
                         let opcode = match details.operation {
                             1 => Opcode::LD,
                             2 => Opcode::SD,
@@ -208,22 +229,13 @@ impl MinimalExecutorRunner {
                                 return Ok(None);
                             }
                             // The child terminates with some errors. We still want to process logs.
-                            self.process
-                                .take()
-                                .unwrap()
-                                .1
-                                .join()
-                                .expect("wait for log thread to finish");
+                            let (_, log_thread, killed_by_monitor) = self.process.take().unwrap();
+                            log_thread.join().expect("wait for log thread to finish");
                             // Child process is terminated, let's find out why
                             if status.signal() == Some(libc::SIGBUS) {
                                 tracing::warn!("SIGBUS signal is received, there is a chance /dev/shm is full!");
                             }
-                            let error = match (status.code(), status.signal()) {
-                                (_, Some(libc::SIGKILL)) => ExecutionError::TooMuchMemory(),
-                                // SIGILL via exit status, if the crash channel missed it.
-                                (_, Some(libc::SIGILL)) => ExecutionError::Unimplemented(),
-                                (code, signal) => ExecutionError::Other(format!("Child native executor terminates early, code: {code:?}, signal: {signal:?}")),
-                            };
+                            let error = child_exit_error(&status, &killed_by_monitor);
                             self.output = Some(Err(error.clone()));
                             return Err(error);
                         }
@@ -241,7 +253,7 @@ impl MinimalExecutorRunner {
 
     fn wait_for_success(&mut self) -> Result<(), ExecutionError> {
         // SP1 program terminates, wait for output and terminate child process.
-        let (mut child, log_thread) = self.process.take().unwrap();
+        let (mut child, log_thread, killed_by_monitor) = self.process.take().unwrap();
         let stdout = child.stdout.take().expect("open stdout");
         let mut stdout_reader = BufReader::new(stdout);
 
@@ -261,13 +273,7 @@ impl MinimalExecutorRunner {
             // Non-tracing runner has no crash handler, so map the exit signal to a
             // typed cause here instead of panicking (mirrors the Timeout branch).
             _ => {
-                let error = match (status.code(), status.signal()) {
-                    (_, Some(libc::SIGKILL)) => ExecutionError::TooMuchMemory(),
-                    (_, Some(libc::SIGILL)) => ExecutionError::Unimplemented(),
-                    (code, signal) => ExecutionError::Other(format!(
-                        "Child native executor terminated abnormally, code: {code:?}, signal: {signal:?}"
-                    )),
-                };
+                let error = child_exit_error(&status, &killed_by_monitor);
                 self.output = Some(Err(error.clone()));
                 Err(error)
             }
@@ -389,7 +395,7 @@ impl MinimalExecutorRunner {
     }
 
     pub fn reset(&mut self) {
-        if let Some((mut child, _)) = self.process.take() {
+        if let Some((mut child, _, _)) = self.process.take() {
             child.kill().expect("running child cannot be killed");
         }
         self.output = None;
@@ -425,8 +431,32 @@ fn create(input: &Input) -> (SharedMemory, Option<ShmTraceRing>) {
     (memory, consumer)
 }
 
+/// Maps a dead child's exit status to a typed [`ExecutionError`] instead of panicking.
+///
+/// A `SIGKILL` is split by `killed_by_monitor`: if our RSS monitor sent it, the program
+/// exceeded its budget ([`ExecutionError::TooMuchMemory`]); otherwise it was an external
+/// kill, e.g. the OS OOM-killer ([`ExecutionError::ChildKilled`]).
+fn child_exit_error(
+    status: &std::process::ExitStatus,
+    killed_by_monitor: &AtomicBool,
+) -> ExecutionError {
+    match (status.code(), status.signal()) {
+        (_, Some(libc::SIGKILL)) if killed_by_monitor.load(Ordering::SeqCst) => {
+            ExecutionError::TooMuchMemory()
+        }
+        (_, Some(libc::SIGKILL)) => ExecutionError::ChildKilled(),
+        (_, Some(libc::SIGILL)) => ExecutionError::Unimplemented(),
+        (code, signal) => ExecutionError::Other(format!(
+            "Child native executor terminated abnormally, code: {code:?}, signal: {signal:?}"
+        )),
+    }
+}
+
 /// Spawns a process with piped I/O and an RSS memory monitor thread.
-fn spawn_restricted(mut cmd: Command, limit_bytes: u64) -> std::io::Result<Child> {
+fn spawn_restricted(
+    mut cmd: Command,
+    limit_bytes: u64,
+) -> std::io::Result<(Child, Arc<AtomicBool>)> {
     cmd.stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
 
     // Disable core dumps for the child by temporarily zeroing RLIMIT_CORE in the
@@ -444,6 +474,9 @@ fn spawn_restricted(mut cmd: Command, limit_bytes: u64) -> std::io::Result<Child
     }?;
     let child_pid = child.id();
 
+    let killed_by_monitor = Arc::new(AtomicBool::new(false));
+    let monitor_flag = killed_by_monitor.clone();
+
     // Start the Background Memory Monitor (The Enforcer)
     thread::spawn(move || {
         let mut sys = System::new();
@@ -468,6 +501,8 @@ fn spawn_restricted(mut cmd: Command, limit_bytes: u64) -> std::io::Result<Child
                         limit_bytes / 1024 / 1024
                     );
 
+                    // Flag before killing so the kill is attributable to us, not the OOM-killer.
+                    monitor_flag.store(true, Ordering::SeqCst);
                     // Kill the process immediately
                     unsafe {
                         libc::kill(child_pid as i32, libc::SIGKILL);
@@ -478,13 +513,54 @@ fn spawn_restricted(mut cmd: Command, limit_bytes: u64) -> std::io::Result<Child
             thread::sleep(poll_interval);
         }
     });
-    Ok(child)
+    Ok((child, killed_by_monitor))
 }
 
 impl Drop for MinimalExecutorRunner {
     fn drop(&mut self) {
-        if let Some((mut child, _)) = self.process.take() {
+        if let Some((mut child, _, _)) = self.process.take() {
             let _ = child.kill();
         }
     }
 }
+
+#[cfg(test)]
+mod child_exit_error_tests {
+    use super::child_exit_error;
+    use sp1_core_executor::ExecutionError;
+    use std::os::unix::process::ExitStatusExt;
+    use std::process::ExitStatus;
+    use std::sync::atomic::AtomicBool;
+
+    // A wait()-style status for a process killed by `signal` (low 7 bits on Unix).
+    fn signaled(signal: i32) -> ExitStatus {
+        ExitStatus::from_raw(signal)
+    }
+
+    #[test]
+    fn sigkill_by_our_monitor_is_too_much_memory() {
+        let flag = AtomicBool::new(true); // our RSS monitor sent the SIGKILL
+        assert!(matches!(
+            child_exit_error(&signaled(libc::SIGKILL), &flag),
+            ExecutionError::TooMuchMemory()
+        ));
+    }
+
+    #[test]
+    fn external_sigkill_is_child_killed() {
+        let flag = AtomicBool::new(false); // OOM-killer / external SIGKILL
+        assert!(matches!(
+            child_exit_error(&signaled(libc::SIGKILL), &flag),
+            ExecutionError::ChildKilled()
+        ));
+    }
+
+    #[test]
+    fn sigill_is_unimplemented() {
+        let flag = AtomicBool::new(false);
+        assert!(matches!(
+            child_exit_error(&signaled(libc::SIGILL), &flag),
+            ExecutionError::Unimplemented()
+        ));
+    }
+}
```
