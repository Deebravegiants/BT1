# [?] apollo_node: fix awk print race condition in integration test stdout (#11420)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-01-06
Source: https://github.com/starkware-libs/sequencer/commit/10c181fe4416625891ae1a7ffd0af332a0fe05d1
Type: security-commit

## Details
apollo_node: fix awk print race condition in integration test stdout (#11420)

## Patch
### crates/apollo_node/src/test_utils/node_runner.rs
```diff
@@ -1,6 +1,8 @@
 use std::fs::create_dir_all;
+use std::io::{stdout, Stdout, Write};
 use std::path::PathBuf;
 use std::process::Stdio;
+use std::sync::{Mutex, OnceLock};
 
 use apollo_config::CONFIG_FILE_ARG;
 use apollo_infra_utils::command::create_shell_command;
@@ -15,6 +17,30 @@ use tracing::{error, info, instrument};
 pub const NODE_EXECUTABLE_PATH: &str = "target/debug/apollo_node";
 const TEMP_LOGS_DIR: &str = "integration_test_temporary_logs";
 
+/// Global synchronized stdout writer to prevent race conditions when multiple
+/// node processes write their annotated output concurrently.
+static STDOUT_WRITER: OnceLock<Mutex<Stdout>> = OnceLock::new();
+
+fn get_stdout_writer() -> &'static Mutex<Stdout> {
+    STDOUT_WRITER.get_or_init(|| Mutex::new(stdout()))
+}
+
+/// Writes an annotated line to stdout atomically (with synchronization).
+fn write_annotated_stdout_line(prefix: &str, line: &str) {
+    let writer = get_stdout_writer();
+    if let Ok(mut stdout) = writer.lock() {
+        writeln!(stdout, "{} {}", prefix, line).expect("Should be able to write to stdout.");
+        stdout.flush().expect("Should be able to flush stdout.");
+    }
+}
+
+/// Writes a line with a newline to an async file.
+async fn write_file_line(file: &mut File, line: &str) {
+    if let Err(e) = file.write_all(format!("{line}\n").as_bytes()).await {
+        error!("Failed to write to file: {}", e);
+    }
+}
+
 #[derive(Debug, Clone)]
 pub struct NodeRunner {
     node_index: usize,
@@ -44,7 +70,7 @@ pub fn spawn_run_node(
     AbortOnDropHandle::new(task::spawn(async move {
         info!("Running the node from its spawned task.");
         // Obtain handles, as the processes and task are terminated when their handles are dropped.
-        let (mut node_handle, _annotator_handle, _pipe_task) =
+        let (mut node_handle, _pipe_task) =
             spawn_node_child_process(node_config_paths, node_runner.clone()).await;
         let _node_run_result = node_handle.
             wait(). // Runs the node until completion, should be running indefinitely.
@@ -57,7 +83,7 @@ pub fn spawn_run_node(
 async fn spawn_node_child_process(
     node_config_paths: Vec<PathBuf>,
     node_runner: NodeRunner,
-) -> (Child, Child, AbortOnDropHandle<()>) {
+) -> (Child, AbortOnDropHandle<()>) {
     info!("Getting the node executable.");
     let node_executable = get_node_executable_path();
 
@@ -78,26 +104,18 @@ async fn spawn_node_child_process(
         .spawn()
         .expect("Spawning sequencer node should succeed.");
 
-    let mut annotator_process: Child = create_shell_command("awk")
-        .arg("-v")
-        // Print the prefix in different colors.
-        .arg(format!("prefix=\u{1b}[3{}m{}\u{1b}[0m", node_runner.node_index+1, node_runner.get_description()))
-        .arg("{print prefix, $0}")
-        .stdin(std::process::Stdio::piped())
-        .stderr(Stdio::inherit())
-        .stdout(Stdio::inherit())
-        .kill_on_drop(true) // Required for stopping when the handle is dropped.
-        .spawn()
-        .expect("Spawning node output annotation should succeed.");
-
-    info!("Node PID: {:?}, Annotator PID: {:?}", node_process.id(), annotator_process.id());
+    // Print the prefix in different colors.
+    let prefix = format!(
+        "\u{1b}[3{}m{}\u{1b}[0m",
+        node_runner.node_index + 1,
+        node_runner.get_description()
+    );
+    info!("Node PID: {:?}", node_process.id());
 
-    // Get the node stdout and the annotator stdin.
+    // Get the node stdout.
     let node_stdout = node_process.stdout.take().expect("Node stdout should be available.");
-    let mut annotator_stdin =
-        annotator_process.stdin.take().expect("Annotator stdin should be available.");
 
-    // Spawn a task to connect the node stdout with the annotator stdin.
+    // Spawn a task to read node stdout and write to both file and synchronized stdout.
     let pipe_task = AbortOnDropHandle::new(tokio::spawn(async move {
         let mut reader = BufReader::new(node_stdout).lines();
         info!("Writing node logs to file: {:?}", node_runner.logs_file_path());
@@ -106,35 +124,20 @@ async fn spawn_node_child_process(
         while let Some(line) = reader.next_line().await.transpose() {
             match line {
                 Ok(line) => {
-                    // Write to annotator stdin
-                    if let Err(e) = annotator_stdin.write_all(line.as_bytes()).await {
-                        error!("Failed to write to annotator stdin: {}", e);
-                    }
-                    if let Err(e) = annotator_stdin.write_all(b"\n").await {
-                        error!("Failed to write newline to annotator stdin: {}", e);
-                    }
-
-                    // Write to file
-                    if let Err(e) = file.write_all(line.as_bytes()).await {
-                        error!("Failed to write to file: {}", e);
-                    }
-                    if let Err(e) = file.write_all(b"\n").await {
-                        error!("Failed to write newline to file: {}", e);
-                    }
+                    // Write annotated line to synchronized stdout.
+                    write_annotated_stdout_line(&prefix, &line);
+
+                    // Write to file.
+                    write_file_line(&mut file, &line).await;
                 }
                 Err(e) => {
                     error!("Error while reading node stdout: {}", e);
                 }
             }
         }
-
-        // Close the annotator stdin when done.
-        if let Err(e) = annotator_stdin.shutdown().await {
-            error!("Failed to shut down annotator stdin: {}", e);
-        }
     }));
 
-    (node_process, annotator_process, pipe_task)
+    (node_process, pipe_task)
 }
 
 pub fn get_node_executable_path() -> String {
```
