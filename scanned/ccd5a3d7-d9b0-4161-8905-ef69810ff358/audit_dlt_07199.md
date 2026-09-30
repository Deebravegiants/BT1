# [?] fix(test): Show full Zebra test panic details in CI logs (#4942)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2022-08-28
Source: https://github.com/ZcashFoundation/zebra/commit/f46d0115e5cec2265adb0e1331e01c330b45d4f4
Type: security-commit

## Details
fix(test): Show full Zebra test panic details in CI logs (#4942)

* Handle test failure regexes using Result::Err, rather than panicking

* Add output logs to test context, and add tests for that

* Let empty test child logs be read again (and produce empty output)

* Ignore missing test children when killing with ignore_exited

* Fix a clippy lint

* Rename `line` to `line_result` for clarity

* Revert a redundant context_from() on kill()

* Only ignore "no such process" kill() errors in sync_until() tests

* Log the command timeout when an acceptance test fails

* fix clippy

Co-authored-by: Alfredo Garcia <oxarbitrage@gmail.com>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -6544,6 +6544,7 @@ dependencies = [
  "color-eyre",
  "futures",
  "hex",
+ "humantime",
  "indexmap",
  "insta",
  "lazy_static",
```

### zebra-test/Cargo.toml
```diff
@@ -26,9 +26,11 @@ color-eyre = "0.6.1"
 # Enable a feature that makes tinyvec compile much faster.
 tinyvec = { version = "1.6.0", features = ["rustc_1_55"] }
 
+humantime = "2.1.0"
 owo-colors = "3.4.0"
 spandoc = "0.2.2"
 thiserror = "1.0.32"
+
 tracing-subscriber = { version = "0.3.11", features = ["env-filter"] }
 tracing-error = "0.2.0"
 tracing = "0.1.31"
```

### zebra-test/src/command.rs
```diff
@@ -3,7 +3,7 @@
 use std::{
     convert::Infallible as NoDir,
     fmt::{self, Debug, Write as _},
-    io::{BufRead, BufReader, Read, Write as _},
+    io::{BufRead, BufReader, ErrorKind, Read, Write as _},
     path::Path,
     process::{Child, Command, ExitStatus, Output, Stdio},
     time::{Duration, Instant},
@@ -107,6 +107,7 @@ impl CommandExt for Command {
             failure_regexes: RegexSet::empty(),
             ignore_regexes: RegexSet::empty(),
             deadline: None,
+            timeout: None,
             bypass_test_capture: false,
         })
     }
@@ -221,59 +222,73 @@ pub struct TestChild<T> {
     /// Only checked when the command outputs each new line (#1140).
     pub deadline: Option<Instant>,
 
+    /// The timeout for this command to finish.
+    ///
+    /// Only used for debugging output.
+    pub timeout: Option<Duration>,
+
     /// If true, write child output directly to standard output,
     /// bypassing the Rust test harness output capture.
     bypass_test_capture: bool,
 }
 
 /// Checks command output log `line` from `cmd` against a `failure_regexes` regex set,
-/// and panics if any regex matches. The line is skipped if it matches `ignore_regexes`.
-///
-/// # Panics
+/// and returns an error if any regex matches. The line is skipped if it matches `ignore_regexes`.
 ///
-/// - if any stdout or stderr lines match any failure regex, but do not match any ignore regex
+/// Passes through errors from the underlying reader.
 pub fn check_failure_regexes(
-    line: &std::io::Result<String>,
+    line: std::io::Result<String>,
     failure_regexes: &RegexSet,
     ignore_regexes: &RegexSet,
     cmd: &str,
     bypass_test_capture: bool,
-) {
-    if let Ok(line) = line {
-        let ignore_matches = ignore_regexes.matches(line);
-        let ignore_matches: Vec<&str> = ignore_matches
-            .iter()
-            .map(|index| ignore_regexes.patterns()[index].as_str())
-            .collect();
-
-        let failure_matches = failure_regexes.matches(line);
-        let failure_matches: Vec<&str> = failure_matches
-            .iter()
-            .map(|index| failure_regexes.patterns()[index].as_str())
-            .collect();
-
-        if !ignore_matches.is_empty() {
-            let ignore_matches = ignore_matches.join(",");
-
-            let ignore_msg = if failure_matches.is_empty() {
-                format!(
-                    "Log matched ignore regexes: {:?}, but no failure regexes",
-                    ignore_matches,
-                )
-            } else {
-                let failure_matches = failure_matches.join(",");
-                format!(
-                    "Ignoring failure regexes: {:?}, because log matched ignore regexes: {:?}",
-                    failure_matches, ignore_matches,
-                )
-            };
+) -> std::io::Result<String> {
+    let line = line?;
+
+    // Check if the line matches any patterns
+    let ignore_matches = ignore_regexes.matches(&line);
+    let ignore_matches: Vec<&str> = ignore_matches
+        .iter()
+        .map(|index| ignore_regexes.patterns()[index].as_str())
+        .collect();
+
+    let failure_matches = failure_regexes.matches(&line);
+    let failure_matches: Vec<&str> = failure_matches
+        .iter()
+        .map(|index| failure_regexes.patterns()[index].as_str())
+        .collect();
+
+    // If we match an ignore pattern, ignore any failure matches
+    if !ignore_matches.is_empty() {
+        let ignore_matches = ignore_matches.join(",");
+
+        let ignore_msg = if failure_matches.is_empty() {
+            format!(
+                "Log matched ignore regexes: {:?}, but no failure regexes",
+                ignore_matches,
+            )
+        } else {
+            let failure_matches = failure_matches.join(",");
+            format!(
+                "Ignoring failure regexes: {:?}, because log matched ignore regexes: {:?}",
+                failure_matches, ignore_matches,
+            )
+        };
 
-            write_to_test_logs(ignore_msg, bypass_test_capture);
-            return;
-        }
+        write_to_test_logs(ignore_msg, bypass_test_capture);
+
+        return Ok(line);
+    }
+
+    // If there were no failures, pass the log line through
+    if failure_matches.is_empty() {
+        return Ok(line);
+    }
 
-        assert!(
-            failure_matches.is_empty(),
+    // Otherwise, if the process logged a failure message, return an error
+    let error = std::io::Error::new(
+        ErrorKind::Other,
+        format!(
             "test command:\n\
              {cmd}\n\n\
              Logged a failure message:\n\
@@ -283,8 +298,10 @@ pub fn check_failure_regexes(
              All Failure regexes: \
              {:#?}\n",
             failure_regexes.patterns(),
-        );
-    }
+        ),
+    );
+
+    Err(error)
 }
 
 /// Write `line` to stdout, so it can be seen in the test logs.
@@ -444,7 +461,7 @@ impl<T> TestChild<T> {
         let bypass_test_capture = self.bypass_test_capture;
 
         let reader = BufReader::new(reader);
-        let lines = BufRead::lines(reader).inspect(move |line| {
+        let lines = BufRead::lines(reader).map(move |line| {
             check_failure_regexes(
                 line,
                 &failure_regexes,
@@ -459,32 +476,62 @@ impl<T> TestChild<T> {
 
     /// Kill the child process.
     ///
+    /// If `ignore_exited` is `true`, log "can't kill an exited process" errors,
+    /// rather than returning them.
+    ///
+    /// Returns the result of the kill.
+    ///
     /// ## BUGS
     ///
     /// On Windows (and possibly macOS), this function can return `Ok` for
     /// processes that have panicked. See #1781.
     #[spandoc::spandoc]
-    pub fn kill(&mut self) -> Result<()> {
+    pub fn kill(&mut self, ignore_exited: bool) -> Result<()> {
         let child = match self.child.as_mut() {
             Some(child) => child,
-            None => return Err(eyre!("child was already taken")).context_from(self.as_mut()),
+            None if ignore_exited => {
+                Self::write_to_test_logs(
+                    "test child was already taken\n\
+                     ignoring kill because ignore_exited is true",
+                    self.bypass_test_capture,
+                );
+                return Ok(());
+            }
+            None => {
+                return Err(eyre!(
+                    "test child was already taken\n\
+                     call kill() once for each child process, or set ignore_exited to true"
+                ))
+                .context_from(self.as_mut())
+            }
         };
 
         /// SPANDOC: Killing child process
-        child.kill().context_from(self.as_mut())?;
+        let kill_result = child.kill().or_else(|error| {
+            if ignore_exited && error.kind() == ErrorKind::InvalidInput {
+                Ok(())
+            } else {
+                Err(error)
+            }
+        });
+
+        kill_result.context_from(self.as_mut())?;
 
         Ok(())
     }
 
     /// Kill the process, and consume all its remaining output.
     ///
+    /// If `ignore_exited` is `true`, log "can't kill an exited process" errors,
+    /// rather than returning them.
+    ///
     /// Returns the result of the kill.
-    pub fn kill_and_consume_output(&mut self) -> Result<()> {
+    pub fn kill_and_consume_output(&mut self, ignore_exited: bool) -> Result<()> {
         self.apply_failure_regexes_to_outputs();
 
         // Prevent a hang when consuming output,
         // by making sure the child's output actually finishes.
-        let kill_result = self.kill();
+        let kill_result = self.kill(ignore_exited);
 
         // Read unread child output.
         //
@@ -496,7 +543,7 @@ impl<T> TestChild<T> {
 
             if wrote_lines {
                 // Write an empty line, to make output more readable
-                self.write_to_test_logs("");
+                Self::write_to_test_logs("", self.bypass_test_capture);
             }
         }
 
@@ -506,7 +553,7 @@ impl<T> TestChild<T> {
             while self.wait_for_stderr_line(None) {}
 
             if wrote_lines {
-                self.write_to_test_logs("");
+                Self::write_to_test_logs("", self.bypass_test_capture);
             }
         }
 
@@ -526,12 +573,19 @@ impl<T> TestChild<T> {
     {
         self.apply_failure_regexes_to_outputs();
 
-        if let Some(Ok(line)) = self.stdout.as_mut().and_then(|iter| iter.next()) {
+        if let Some(line_result) = self.stdout.as_mut().and_then(|iter| iter.next()) {
+            let bypass_test_capture = self.bypass_test_capture;
+
             if let Some(write_context) = write_context.into() {
-                self.write_to_test_logs(write_context);
+                Self::write_to_test_logs(write_context, bypass_test_capture);
             }
 
-            self.write_to_test_logs(line);
+            Self::write_to_test_logs(
+                line_result
+                    .context_from(self)
+                    .expect("failure reading test process logs"),
+                bypass_test_capture,
+            );
 
             return true;
         }
@@ -552,12 +606,19 @@ impl<T> TestChild<T> {
     {
         self.apply_failure_regexes_to_outputs();
 
-        if let Some(Ok(line)) = self.stderr.as_mut().and_then(|iter| iter.next()) {
+        if let Some(line_result) = self.stderr.as_mut().and_then(|iter| iter.next()) {
+            let bypass_test_capture = self.bypass_test_capture;
+
             if let Some(write_context) = write_context.into() {
-                self.write_to_test_logs(write_context);
+                Self::write_to_test_logs(write_context, bypass_test_capture);
             }
 
-            self.write_to_test_logs(line);
+            Self::write_to_test_logs(
+                line_result
+                    .context_from(self)
+                    .expect("failure reading test process logs"),
+                bypass_test_capture,
+            );
 
             return true;
         }
@@ -583,8 +644,8 @@ impl<T> TestChild<T> {
             // either in `context_from`, or on drop.
             None => {
                 return Err(eyre!(
-                    "child was already taken.\n\
-                 wait_with_output can only be called once for each child process",
+                    "test child was already taken\n\
+                     wait_with_output can only be called once for each child process",
                 ))
                 .context_from(self.as_mut())
             }
@@ -623,7 +684,9 @@ impl<T> TestChild<T> {
     ///
     /// Does not apply to `wait_with_output`.
     pub fn with_timeout(mut self, timeout: Duration) -> Self {
+        self.timeout = Some(timeout);
         self.deadline = Some(Instant::now() + timeout);
+
         self
     }
 
@@ -654,10 +717,15 @@ impl<T> TestChild<T> {
 
         match self.expect_line_matching_regex_set(&mut lines, success_regex, "stdout") {
             Ok(()) => {
+                // Replace the log lines for the next check
                 self.stdout = Some(lines);
                 Ok(self)
             }
-            Err(report) => Err(report),
+            Err(report) => {
+                // Read all the log lines for error context
+                self.stdout = Some(lines);
+                Err(report).context_from(self)
+            }
         }
     }
 
@@ -681,10 +749,15 @@ impl<T> TestChild<T> {
 
         match self.expect_line_matching_regex_set(&mut lines, success_regex, "stderr") {
             Ok(()) => {
+                // Replace the log lines for the next check
                 self.stderr = Some(lines);
                 Ok(self)
             }
-            Err(report) => Err(report),
+            Err(report) => {
+                // Read all the log lines for error context
+                self.stderr = Some(lines);
+                Err(report).context_from(self)
+            }
         }
     }
 
@@ -739,6 +812,7 @@ impl<T> TestChild<T> {
     /// Note: the timeout is only checked after each full line is received from
     /// the child (#1140).
     #[instrument(skip(self, lines))]
+    #[allow(clippy::unwrap_in_result)]
     pub fn expect_line_matching_regexes<L>(
         &mut self,
         lines: &mut L,
@@ -762,7 +836,7 @@ impl<T> TestChild<T> {
             };
 
             // Since we're about to discard this line write it to stdout.
-            self.write_to_test_logs(&line);
+            Self::write_to_test_logs(&line, self.bypass_test_capture);
 
             if success_regexes.is_match(&line) {
                 return Ok(());
@@ -771,16 +845,20 @@ impl<T> TestChild<T> {
 
         if self.is_running() {
             // If the process exits between is_running and kill, we will see
-            // spurious errors here. If that happens, ignore "no such process"
+            // spurious errors here. So we want to ignore "no such process"
             // errors from kill.
-            self.kill()?;
+            self.kill(true)?;
         }
 
+        let timeout =
+            humantime::format_duration(self.timeout.expect("already checked past_deadline()"));
+
         let report = eyre!(
-            "{} of command did not contain any matches for the given regex",
-            stream_name
+            "{} of command did not log any matches for the given regex,\n\
+             within the {:?} command timeout",
+            stream_name,
+            timeout,
         )
-        .context_from(self)
         .with_section(|| format!("{:#?}", success_regexes.patterns()).header("Match Regex:"));
 
         Err(report)
@@ -794,11 +872,11 @@ impl<T> TestChild<T> {
     /// May cause weird reordering for stdout / stderr.
     /// Uses stdout even if the original lines were from stderr.
     #[allow(clippy::print_stdout)]
-    fn write_to_test_logs<S>(&self, line: S)
+    fn write_to_test_logs<S>(line: S, bypass_test_capture: bool)
     where
         S: AsRef<str>,
     {
-        write_to_test_logs(line, self.bypass_test_capture);
+        write_to_test_logs(line, bypass_test_capture);
     }
 
     /// Kill `child`, wait for its output, and use that output as the context for
@@ -814,7 +892,7 @@ impl<T> TestChild<T> {
         };
 
         if self.is_running() {
-            let kill_res = self.kill();
+            let kill_res = self.kill(true);
             if let Err(kill_err) = kill_res {
                 error = error.wrap_err(kill_err);
             }
@@ -872,9 +950,8 @@ impl<T> Drop for TestChild<T> {
     fn drop(&mut self) {
         // Clean up child processes when the test finishes,
         // and check for failure logs.
-        //
-        // We don't care about the kill result here.
-        let _ = self.kill_and_consume_output();
+        self.kill_and_consume_output(true)
+            .expect("failure reading test process logs")
     }
 }
 
@@ -1198,7 +1275,9 @@ impl<T> ContextFrom<&mut TestChild<T>> for Report {
 
         if let Some(stdout) = &mut source.stdout {
             for line in stdout {
-                let line = if let Ok(line) = line { line } else { break };
+                let line = line.unwrap_or_else(|error| {
+                    format!("failure reading test process logs: {:?}", error)
+                });
                 let _ = writeln!(&mut stdout_buf, "{}", line);
             }
         } else if let Some(child) = &mut source.child {
@@ -1209,7 +1288,9 @@ impl<T> ContextFrom<&mut TestChild<T>> for Report {
 
         if let Some(stderr) = &mut source.stderr {
             for line in stderr {
-                let line = if let Ok(line) = line { line } else { break };
+                let line = line.unwrap_or_else(|error| {
+                    format!("failure reading test process logs: {:?}", error)
+                });
                 let _ = writeln!(&mut stderr_buf, "{}", line);
             }
         } else if let Some(child) = &mut source.child {
```

### zebra-test/tests/command.rs
```diff
@@ -185,19 +185,15 @@ fn kill_on_timeout_no_output() -> Result<()> {
 }
 
 /// Make sure failure regexes detect when a child process prints a failure message to stdout,
-/// and panic with a test failure message.
+/// and fail with a test failure message.
 #[test]
-#[should_panic(expected = "Logged a failure message")]
 fn failure_regex_matches_stdout_failure_message() {
     let _init_guard = zebra_test::init();
 
     const TEST_CMD: &str = "echo";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &[]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     let mut child = tempdir()
@@ -209,15 +205,21 @@ fn failure_regex_matches_stdout_failure_message() {
 
     // Any method that reads output should work here.
     // We use a non-matching regex, to trigger the failure panic.
-    child
+    let expected_error = child
         .expect_stdout_line_matches("this regex should not match")
         .unwrap_err();
+
+    let expected_error = format!("{:?}", expected_error);
+    assert!(
+        expected_error.contains("Logged a failure message"),
+        "error did not contain expected failure message: {}",
+        expected_error,
+    );
 }
 
 /// Make sure failure regexes detect when a child process prints a failure message to stderr,
 /// and panic with a test failure message.
 #[test]
-#[should_panic(expected = "Logged a failure message")]
 fn failure_regex_matches_stderr_failure_message() {
     let _init_guard = zebra_test::init();
 
@@ -230,10 +232,7 @@ fn failure_regex_matches_stderr_failure_message() {
     const TEST_CMD: &str = "bash";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &["-c", "read -t 1 -p failure_message"]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     let mut child = tempdir()
@@ -245,9 +244,16 @@ fn failure_regex_matches_stderr_failure_message() {
 
     // Any method that reads output should work here.
     // We use a non-matching regex, to trigger the failure panic.
-    child
+    let expected_error = child
         .expect_stderr_line_matches("this regex should not match")
         .unwrap_err();
+
+    let expected_error = format!("{:?}", expected_error);
+    assert!(
+        expected_error.contains("Logged a failure message"),
+        "error did not contain expected failure message: {}",
+        expected_error,
+    );
 }
 
 /// Make sure failure regexes detect when a child process prints a failure message to stdout,
@@ -260,10 +266,7 @@ fn failure_regex_matches_stdout_failure_message_drop() {
     const TEST_CMD: &str = "echo";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &[]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     let _child = tempdir()
@@ -279,6 +282,84 @@ fn failure_regex_matches_stdout_failure_message_drop() {
     // Drop should read all unread output.
 }
 
+/// When checking output, make sure failure regexes detect when a child process
+/// prints a failure message to stdout, then they fail the test,
+/// and read any extra multi-line output from the child process.
+#[test]
+fn failure_regex_reads_multi_line_output_on_expect_line() {
+    let _init_guard = zebra_test::init();
+
+    const TEST_CMD: &str = "echo";
+    // Skip the test if the test system does not have the command
+    if !is_command_available(TEST_CMD, &[]) {
+        return;
+    }
+
+    let mut child = tempdir()
+        .unwrap()
+        .spawn_child_with_command(
+            TEST_CMD,
+            args![
+                "failure_message\n\
+                 multi-line failure message"
+            ],
+        )
+        .unwrap()
+        .with_timeout(Duration::from_secs(5))
+        .with_failure_regex_set("failure_message", RegexSet::empty());
+
+    // Any method that reads output should work here.
+    // We use a non-matching regex, to trigger the failure panic.
+    let expected_error = child
+        .expect_stdout_line_matches("this regex should not match")
+        .unwrap_err();
+
+    let expected_error = format!("{:?}", expected_error);
+    assert!(
+        expected_error.contains(
+            "\
+Unread Stdout:
+   multi-line failure message\
+            "
+        ),
+        "error did not contain expected failure message: {}",
+        expected_error,
+    );
+}
+
+/// On drop, make sure failure regexes detect when a child process prints a failure message.
+/// then they fail the test, and read any extra multi-line output from the child process.
+#[test]
+#[should_panic(expected = "Unread Stdout:
+   multi-line failure message")]
+fn failure_regex_reads_multi_line_output_on_drop() {
+    let _init_guard = zebra_test::init();
+
+    const TEST_CMD: &str = "echo";
+    // Skip the test if the test system does not have the command
+    if !is_command_available(TEST_CMD, &[]) {
+        return;
+    }
+
+    let _child = tempdir()
+        .unwrap()
+        .spawn_child_with_command(
+            TEST_CMD,
+            args![
+                "failure_message\n\
+                 multi-line failure message"
+            ],
+        )
+        .unwrap()
+        .with_timeout(Duration::from_secs(5))
+        .with_failure_regex_set("failure_message", RegexSet::empty());
+
+    // Give the child process enough time to print its output.
+    std::thread::sleep(Duration::from_secs(1));
+
+    // Drop should read all unread output.
+}
+
 /// Make sure failure regexes detect when a child process prints a failure message to stdout,
 /// then the child process is killed.
 #[test]
@@ -289,10 +370,7 @@ fn failure_regex_matches_stdout_failure_message_kill() {
     const TEST_CMD: &str = "echo";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &[]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     let mut child = tempdir()
@@ -307,7 +385,7 @@ fn failure_regex_matches_stdout_failure_message_kill() {
 
     // Kill should read all unread output to generate the error context,
     // or the output should be read on drop.
-    child.kill().unwrap();
+    child.kill(true).unwrap();
 }
 
 /// Make sure failure regexes detect when a child process prints a failure message to stdout,
@@ -320,10 +398,7 @@ fn failure_regex_matches_stdout_failure_message_kill_on_error() {
     const TEST_CMD: &str = "echo";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &[]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     let child = tempdir()
@@ -352,10 +427,7 @@ fn failure_regex_matches_stdout_failure_message_no_kill_on_error() {
     const TEST_CMD: &str = "echo";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &[]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     let child = tempdir()
@@ -379,7 +451,6 @@ fn failure_regex_matches_stdout_failure_message_no_kill_on_error() {
 ///
 /// TODO: test the failure regex on timeouts with no output (#1140)
 #[test]
-#[should_panic(expected = "Logged a failure message")]
 fn failure_regex_timeout_continuous_output() {
     let _init_guard = zebra_test::init();
 
@@ -389,10 +460,7 @@ fn failure_regex_timeout_continuous_output() {
     const TEST_CMD: &str = "hexdump";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &["/dev/null"]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     // Without '-v', hexdump hides duplicate lines. But we want duplicate lines
@@ -406,9 +474,16 @@ fn failure_regex_timeout_continuous_output() {
 
     // We need to use expect_stdout_line_matches, because wait_with_output ignores timeouts.
     // We use a non-matching regex, to trigger the timeout and the failure panic.
-    child
+    let expected_error = child
         .expect_stdout_line_matches("this regex should not match")
         .unwrap_err();
+
+    let expected_error = format!("{:?}", expected_error);
+    assert!(
+        expected_error.contains("Logged a failure message"),
+        "error did not contain expected failure message: {}",
+        expected_error,
+    );
 }
 
 /// Make sure failure regexes are checked when a child process prints a failure message to stdout,
@@ -423,10 +498,7 @@ fn failure_regex_matches_stdout_failure_message_wait_for_output() {
     const TEST_CMD: &str = "echo";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &[]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     let child = tempdir()
@@ -447,17 +519,13 @@ fn failure_regex_matches_stdout_failure_message_wait_for_output() {
 /// Make sure failure regex iters detect when a child process prints a failure message to stdout,
 /// and panic with a test failure message.
 #[test]
-#[should_panic(expected = "Logged a failure message")]
 fn failure_regex_iter_matches_stdout_failure_message() {
     let _init_guard = zebra_test::init();
 
     const TEST_CMD: &str = "echo";
     // Skip the test if the test system does not have the command
     if !is_command_available(TEST_CMD, &[]) {
-        panic!(
-            "skipping test: command not available\n\
-             fake panic message: Logged a failure message"
-        );
+        return;
     }
 
     let mut child = tempdir()
@@ -472,9 +540,16 @@ fn failure_regex_iter_matches_stdout_failure_message() {
 
     // Any method that reads output should work here.
     // We use a non-matching regex, to trigger the failure panic.
-    child
+    let expected_error = child
         .expect_stdout_line_matches("this regex should not match")
         .unwrap_err();
+
+    let expected_error = format!("{:?}", expected_error);
+    assert!(
+        expected_error.contains("Logged a failure message"),
+        "error did not contain expected failure message: {}",
+        expected_error,
+    );
 }
 
 /// Make sure ignore regexes override failure regexes.
```

### zebrad/tests/acceptance.rs
```diff
@@ -258,7 +258,7 @@ fn start_no_args() -> Result<()> {
 
     // Run the program and kill it after a few seconds
     std::thread::sleep(LAUNCH_DELAY);
-    child.kill()?;
+    child.kill(false)?;
 
     let output = child.wait_with_output()?;
     let output = output.assert_failure()?;
@@ -285,7 +285,7 @@ fn start_args() -> Result<()> {
     let mut child = testdir.spawn_child(args!["start"])?;
     // Run the program and kill it after a few seconds
     std::thread::sleep(LAUNCH_DELAY);
-    child.kill()?;
+    child.kill(false)?;
     let output = child.wait_with_output()?;
 
     // Make sure the command was killed
@@ -312,7 +312,7 @@ fn persistent_mode() -> Result<()> {
 
     // Run the program and kill it after a few seconds
     std::thread::sleep(LAUNCH_DELAY);
-    child.kill()?;
+    child.kill(false)?;
     let output = child.wait_with_output()?;
 
     // Make sure the command was killed
@@ -380,7 +380,7 @@ fn ephemeral(cache_dir_config: EphemeralConfig, cache_dir_check: EphemeralCheck)
         .spawn_child(args!["start"])?;
     // Run the program and kill it after a few seconds
     std::thread::sleep(LAUNCH_DELAY);
-    child.kill()?;
+    child.kill(false)?;
     let output = child.wait_with_output()?;
 
     // Make sure the command was killed
@@ -547,7 +547,7 @@ fn valid_generated_config(command: &str, expect_stdout_line_contains: &str) -> R
     // Run command using temp dir and kill it after a few seconds
     let mut child = testdir.spawn_child(args![command])?;
     std::thread::sleep(LAUNCH_DELAY);
-    child.kill()?;
+    child.kill(false)?;
 
     let output = child.wait_with_output()?;
     let output = output.assert_failure()?;
@@ -629,8 +629,11 @@ fn invalid_generated_config() -> Result<()> {
     // and terminate.
     std::thread::sleep(Duration::from_secs(2));
     if child.is_running() {
-        child.kill()?;
-        return Err(eyre!("Zebra should not be running anymore."));
+        // We're going to error anyway, so return an error that makes sense to the developer.
+        child.kill(true)?;
+        return Err(eyre!(
+            "Zebra should have exited after reading the invalid config"
+        ));
     }
 
     let output = child.wait_with_output()?;
@@ -654,7 +657,7 @@ fn stored_config_works() -> Result<()> {
     child.expect_stdout_line_matches("Starting zebrad".to_string())?;
 
     // finish
-    child.kill()?;
+    child.kill(false)?;
 
     let output = child.wait_with_output()?;
     let output = output.assert_failure()?;
@@ -1007,7 +1010,7 @@ async fn metrics_endpoint() -> Result<()> {
     assert!(res.status().is_success());
     let body = hyper::body::to_bytes(res).await;
     let (body, mut child) = child.kill_on_error(body)?;
-    child.kill()?;
+    child.kill(false)?;
 
     let output = child.wait_with_output()?;
     let output = output.assert_failure()?;
@@ -1082,7 +1085,7 @@ async fn tracing_endpoint() -> Result<()> {
     let tracing_body = hyper::body::to_bytes(tracing_res).await;
     let (tracing_body, mut child) = child.kill_on_error(tracing_body)?;
 
-    child.kill()?;
+    child.kill(false)?;
 
     let output = child.wait_with_output()?;
     let output = output.assert_failure()?;
@@ -1180,7 +1183,7 @@ async fn rpc_endpoint() -> Result<()> {
     let subversion = parsed["result"]["subversion"].as_str().unwrap();
     assert!(subversion.contains("Zebra"), "Got {}", subversion);
 
-    child.kill()?;
+    child.kill(false)?;
 
     let output = child.wait_with_output()?;
     let output = output.assert_failure()?;
@@ -1503,10 +1506,10 @@ fn lightwalletd_integration_test(test_type: LightwalletdTestType) -> Result<()>
     //
     // zcash/lightwalletd exits by itself, but
     // adityapk00/lightwalletd keeps on going, so it gets killed by the test harness.
-    zebrad.kill()?;
+    zebrad.kill(false)?;
 
     if let Some(mut lightwalletd) = lightwalletd {
-        lightwalletd.kill()?;
+        lightwalletd.kill(false)?;
 
         let lightwalletd_output = lightwalletd.wait_with_output()?.assert_failure()?;
 
@@ -1719,7 +1722,7 @@ where
     // Wait a few seconds and kill first node.
     // Second node is terminated by panic, no need to kill.
     std::thread::sleep(LAUNCH_DELAY);
-    let node1_kill_res = node1.kill();
+    let node1_kill_res = node1.kill(false);
     let (_, mut node2) = node2.kill_on_error(node1_kill_res)?;
 
     // node2 should have panicked due to a conflict. Kill it here anyway, so it
@@ -1872,7 +1875,7 @@ async fn delete_old_databases() -> Result<()> {
     assert!(outside_dir.as_path().exists());
 
     // finish
-    child.kill()?;
+    child.kill(false)?;
 
     let output = child.wait_with_output()?;
     let output = output.assert_failure()?;
```

### zebrad/tests/common/sync.rs
```diff
@@ -250,7 +250,7 @@ pub fn sync_until(
 
         // make sure the child process is dead
         // if it has already exited, ignore that error
-        let _ = child.kill();
+        child.kill(true)?;
 
         Ok(child.dir.take().expect("dir was not already taken"))
     } else {
@@ -393,7 +393,9 @@ pub fn create_cached_database_height(
 
     child.expect_stdout_line_matches(stop_regex)?;
 
-    child.kill()?;
+    // make sure the child process is dead
+    // if it has already exited, ignore that error
+    child.kill(true)?;
 
     Ok(())
 }
```
