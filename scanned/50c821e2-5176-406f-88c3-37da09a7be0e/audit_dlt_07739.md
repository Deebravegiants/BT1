# [?] fix(tracing): return error instead of panicking on log directory creation failure (#22100)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-02-12
Source: https://github.com/paradigmxyz/reth/commit/8a6bbd29fee60743133316e4f8eff80042ecadcd
Type: security-commit

## Details
fix(tracing): return error instead of panicking on log directory creation failure (#22100)

Co-authored-by: Amp <amp@ampcode.com>

## Patch
### crates/tracing/src/layers.rs
```diff
@@ -125,7 +125,7 @@ impl Layers {
         filter: &str,
         file_info: FileInfo,
     ) -> eyre::Result<FileWorkerGuard> {
-        let (writer, guard) = file_info.create_log_writer();
+        let (writer, guard) = file_info.create_log_writer()?;
         let file_filter = build_env_filter(None, filter)?;
         let layer = format.apply(file_filter, None, Some(writer));
         self.add_layer(layer);
@@ -221,32 +221,29 @@ impl FileInfo {
     }
 
     /// Creates the log directory if it doesn't exist.
-    ///
-    /// # Returns
-    /// A reference to the path of the log directory.
-    fn create_log_dir(&self) -> &Path {
+    fn create_log_dir(&self) -> eyre::Result<&Path> {
         let log_dir: &Path = self.dir.as_ref();
         if !log_dir.exists() {
-            std::fs::create_dir_all(log_dir).expect("Could not create log directory");
+            std::fs::create_dir_all(log_dir)
+                .map_err(|err| eyre::eyre!("Could not create log directory {log_dir:?}: {err}"))?;
         }
-        log_dir
+        Ok(log_dir)
     }
 
     /// Creates a non-blocking writer for the log file.
-    ///
-    /// # Returns
-    /// A tuple containing the non-blocking writer and its associated worker guard.
-    fn create_log_writer(&self) -> (tracing_appender::non_blocking::NonBlocking, WorkerGuard) {
-        let log_dir = self.create_log_dir();
+    fn create_log_writer(
+        &self,
+    ) -> eyre::Result<(tracing_appender::non_blocking::NonBlocking, WorkerGuard)> {
+        let log_dir = self.create_log_dir()?;
         let (writer, guard) = tracing_appender::non_blocking(
             RollingFileAppender::new(
                 log_dir.join(&self.file_name),
                 RollingConditionBasic::new().max_size(self.max_size_bytes),
                 self.max_files,
             )
-            .expect("Could not initialize file logging"),
+            .map_err(|err| eyre::eyre!("Could not initialize file logging: {err}"))?,
         );
-        (writer, guard)
+        Ok((writer, guard))
     }
 }
 
```
