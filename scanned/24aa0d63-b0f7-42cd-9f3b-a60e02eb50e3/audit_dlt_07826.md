# [?] Prevent rolling file appender panic (#5117)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2024-01-23
Source: https://github.com/sigp/lighthouse/commit/612eaf2d41b9ca98d7e47b327f4564d41ff24ac9
Type: security-commit

## Details
Prevent rolling file appender panic (#5117)

* rolling file appender panic removal and max log file count

* max log file

## Patch
### common/logging/src/lib.rs
```diff
@@ -10,6 +10,7 @@ use std::io::{Result, Write};
 use std::path::PathBuf;
 use std::time::{Duration, Instant};
 use tracing_appender::non_blocking::NonBlocking;
+use tracing_appender::rolling::{RollingFileAppender, Rotation};
 use tracing_logging_layer::LoggingLayer;
 use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
 
@@ -21,7 +22,6 @@ mod tracing_logging_layer;
 mod tracing_metrics_layer;
 
 pub use sse_logging_components::SSELoggingComponents;
-pub use tracing_logging_layer::cleanup_logging_task;
 pub use tracing_metrics_layer::MetricsLayer;
 
 /// The minimum interval between log messages indicating that a queue is full.
@@ -234,10 +234,27 @@ pub fn create_tracing_layer(base_tracing_log_path: PathBuf, turn_on_terminal_log
         }
     };
 
-    let libp2p_writer =
-        tracing_appender::rolling::daily(base_tracing_log_path.clone(), "libp2p.log");
-    let discv5_writer =
-        tracing_appender::rolling::daily(base_tracing_log_path.clone(), "discv5.log");
+    let Ok(libp2p_writer) = RollingFileAppender::builder()
+        .rotation(Rotation::DAILY)
+        .max_log_files(2)
+        .filename_prefix("libp2p")
+        .filename_suffix("log")
+        .build(base_tracing_log_path.clone())
+    else {
+        eprintln!("Failed to initialize libp2p rolling file appender");
+        return;
+    };
+
+    let Ok(discv5_writer) = RollingFileAppender::builder()
+        .rotation(Rotation::DAILY)
+        .max_log_files(2)
+        .filename_prefix("discv5")
+        .filename_suffix("log")
+        .build(base_tracing_log_path.clone())
+    else {
+        eprintln!("Failed to initialize discv5 rolling file appender");
+        return;
+    };
 
     let (libp2p_non_blocking_writer, libp2p_guard) = NonBlocking::new(libp2p_writer);
     let (discv5_non_blocking_writer, discv5_guard) = NonBlocking::new(discv5_writer);
```

### common/logging/src/tracing_logging_layer.rs
```diff
@@ -1,5 +1,4 @@
-use chrono::{naive::Days, prelude::*};
-use slog::{debug, warn};
+use chrono::prelude::*;
 use std::io::Write;
 use tracing::Subscriber;
 use tracing_appender::non_blocking::{NonBlocking, WorkerGuard};
@@ -55,61 +54,3 @@ impl tracing_core::field::Visit for LogMessageExtractor {
         self.message = format!("{} {:?}", self.message, value);
     }
 }
-
-/// Creates a long lived async task that routinely deletes old tracing log files
-pub async fn cleanup_logging_task(path: std::path::PathBuf, log: slog::Logger) {
-    loop {
-        // Delay for 1 day and then prune old logs
-        tokio::time::sleep(std::time::Duration::from_secs(60 * 60 * 24)).await;
-
-        let Some(yesterday_date) = chrono::prelude::Local::now()
-            .naive_local()
-            .checked_sub_days(Days::new(1))
-        else {
-            warn!(log, "Could not calculate the current date");
-            return;
-        };
-
-        // Search for old log files
-        let dir = path.as_path();
-
-        if dir.is_dir() {
-            let Ok(files) = std::fs::read_dir(dir) else {
-                warn!(log, "Could not read log directory contents"; "path" => ?dir);
-                break;
-            };
-
-            for file in files {
-                let Ok(dir_entry) = file else {
-                    warn!(log, "Could not read file");
-                    continue;
-                };
-
-                let Ok(file_name) = dir_entry.file_name().into_string() else {
-                    warn!(log, "Could not read file"; "file" => ?dir_entry);
-                    continue;
-                };
-
-                if file_name.starts_with("libp2p.log") | file_name.starts_with("discv5.log") {
-                    let log_file_date = file_name.split('.').collect::<Vec<_>>();
-                    if log_file_date.len() == 3 {
-                        let Ok(log_file_date_type) =
-                            NaiveDate::parse_from_str(log_file_date[2], "%Y-%m-%d")
-                        else {
-                            warn!(log, "Could not parse log file date"; "file" => file_name);
-                            continue;
-                        };
-
-                        if log_file_date_type < yesterday_date.into() {
-                            // Delete the file, its too old
-                            debug!(log, "Removing old log file"; "file" => &file_name);
-                            if let Err(e) = std::fs::remove_file(dir_entry.path()) {
-                                warn!(log, "Failed to remove log file"; "file" => file_name, "error" => %e);
-                            }
-                        }
-                    }
-                }
-            }
-        }
-    }
-}
```

### lighthouse/src/main.rs
```diff
@@ -542,13 +542,6 @@ fn run<E: EthSpec>(
 
     let turn_on_terminal_logs = matches.is_present("env_log");
 
-    // Run a task to clean up old tracing logs.
-    let log_cleaner_context = environment.service_context("log_cleaner".to_string());
-    log_cleaner_context.executor.spawn(
-        logging::cleanup_logging_task(path.clone(), log.clone()),
-        "log_cleaner",
-    );
-
     logging::create_tracing_layer(path, turn_on_terminal_logs);
 
     // Allow Prometheus to export the time at which the process was started.
```
