# [?] fix(client): don't panic when logs continue after a top-level instruction returns (#4967)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2026-09-02
Source: https://github.com/otter-sec/anchor/commit/519fc300e2aae4e6dafc23152c328b7b1059345c
Type: security-commit

## Details
fix(client): don't panic when logs continue after a top-level instruction returns (#4967)

## Patch
### CHANGELOG.md
```diff
@@ -48,6 +48,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 - lang: Sync type derives and simplify internal args creation in `declare_program!` ([#4667](https://github.com/solana-foundation/anchor/pull/4667)).
 - lang: Improve `std` hygiene inside macros ([#4700](https://github.com/solana-foundation/anchor/pull/4700)).
 - cli: Honor the SIMD-0431 minimum extend program size when extending program data ([#4785](https://github.com/otter-sec/anchor/pull/4785)).
+- client: Do not panic in `parse_logs_response` when logs continue after a top-level instruction returns, e.g. the runtime's trailing `"Log truncated"` marker ([#4967](https://github.com/solana-foundation/anchor/pull/4967)).
 
 ### Breaking
 
```

### client/src/lib.rs
```diff
@@ -495,18 +495,33 @@ impl Execution {
         })
     }
 
+    /// The program currently on top of the stack.
+    ///
+    /// # Panics
+    ///
+    /// Panics if the stack is empty. Prefer [`Execution::try_program`], which
+    /// returns `None` instead; the stack legitimately empties whenever a
+    /// top-level instruction returns, and more logs can still follow it.
     pub fn program(&self) -> String {
         assert!(!self.stack.is_empty());
         self.stack[self.stack.len() - 1].clone()
     }
 
+    /// The program currently on top of the stack, or `None` when no
+    /// instruction is in scope.
+    pub fn try_program(&self) -> Option<String> {
+        self.stack.last().cloned()
+    }
+
     pub fn push(&mut self, new_program: String) {
         self.stack.push(new_program);
     }
 
+    /// Pops the innermost program off the stack. A no-op when the stack is
+    /// already empty, which happens on a `Program <id> success` line that the
+    /// runtime emits without a matching tracked `invoke`.
     pub fn pop(&mut self) {
-        assert!(!self.stack.is_empty());
-        self.stack.pop().unwrap();
+        self.stack.pop();
     }
 }
 
@@ -890,9 +905,27 @@ fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
             });
 
             while let Some(l) = logs_iter.next() {
+                // No instruction is in scope. This is reached whenever a
+                // top-level instruction has returned but the log stream has
+                // not ended -- most commonly the runtime's trailing
+                // `"Log truncated"` marker, which is appended after the final
+                // `success` when a transaction overruns the log buffer.
+                //
+                // Only a new top-level `invoke [1]` can re-enter a program
+                // context; anything else carries no events, so skip it rather
+                // than panicking in `Execution::program`.
+                let Some(current_program) = execution.try_program() else {
+                    if let Some(caps) = RE.captures(l) {
+                        if &caps[2] == "1" {
+                            execution.push(caps[1].to_string());
+                        }
+                    }
+                    continue;
+                };
+
                 // Parse the log.
                 let (event, new_program, did_pop) = {
-                    if program_id_str == execution.program() {
+                    if program_id_str == current_program {
                         handle_program_log(program_id_str, l)?
                     } else {
                         let (program, did_pop) = handle_system_log(program_id_str, l);
@@ -1166,6 +1199,96 @@ mod tests {
         Ok(())
     }
 
+    #[test]
+    fn execution_pop_past_empty_is_not_a_panic() {
+        let mut logs: &[String] =
+            &["Program term9YPb9mzAsABaqN71A4xdbxHmpBNZavpBiQKZzN3 invoke [1]".to_string()];
+        let mut exe = Execution::new(&mut logs).unwrap();
+        assert_eq!(
+            exe.try_program().as_deref(),
+            Some("term9YPb9mzAsABaqN71A4xdbxHmpBNZavpBiQKZzN3")
+        );
+
+        exe.pop();
+        assert_eq!(exe.try_program(), None);
+
+        // A second pop with nothing left used to trip `assert!(!self.stack.is_empty())`.
+        exe.pop();
+        assert_eq!(exe.try_program(), None);
+    }
+
+    /// Regression for #1941: the runtime appends a bare `"Log truncated"` line
+    /// after the final `success` when a transaction overruns the log buffer.
+    /// That line arrives with an empty stack, and `Execution::program` used to
+    /// panic on it -- taking down the whole `logs_subscribe` thread rather than
+    /// returning an error.
+    #[test]
+    fn test_parse_logs_response_trailing_log_after_last_instruction() -> Result<()> {
+        let logs = [
+            "Program ComputeBudget111111111111111111111111111111 invoke [1]",
+            "Program ComputeBudget111111111111111111111111111111 success",
+            "Log truncated",
+        ];
+        let logs: Vec<String> = logs.iter().map(|&l| l.to_string()).collect();
+
+        let events = parse_logs_response::<MockEvent>(
+            RpcResponse {
+                context: RpcResponseContext::new(0),
+                value: RpcLogsResponse {
+                    signature: "".to_string(),
+                    err: None,
+                    logs,
+                },
+            },
+            "term9YPb9mzAsABaqN71A4xdbxHmpBNZavpBiQKZzN3",
+        )
+        .unwrap();
+
+        assert!(events.is_empty());
+
+        Ok(())
+    }
+
+    /// The empty-stack guard must skip only the logs that carry no events -- a
+    /// later top-level `invoke [1]` still has to re-enter the program context,
+    /// or the fix would trade a panic for silently dropped events.
+    #[test]
+    fn test_parse_logs_response_event_after_trailing_log() -> Result<()> {
+        use {
+            anchor_lang::__private::base64,
+            base64::{engine::general_purpose::STANDARD, Engine},
+        };
+
+        let program_data_log = format!("Program data: {}", STANDARD.encode(MockEvent {}.data()));
+
+        let logs = vec![
+            "Program ComputeBudget111111111111111111111111111111 invoke [1]".to_string(),
+            "Program ComputeBudget111111111111111111111111111111 success".to_string(),
+            // Empty stack from here until the next top-level invoke.
+            "Log truncated".to_string(),
+            "Program term9YPb9mzAsABaqN71A4xdbxHmpBNZavpBiQKZzN3 invoke [1]".to_string(),
+            program_data_log,
+            "Program term9YPb9mzAsABaqN71A4xdbxHmpBNZavpBiQKZzN3 success".to_string(),
+        ];
+
+        let events = parse_logs_response::<MockEvent>(
+            RpcResponse {
+                context: RpcResponseContext::new(0),
+                value: RpcLogsResponse {
+                    signature: "".to_string(),
+                    err: None,
+                    logs,
+                },
+            },
+            "term9YPb9mzAsABaqN71A4xdbxHmpBNZavpBiQKZzN3",
+        )
+        .unwrap();
+
+        assert_eq!(events.len(), 1);
+
+        Ok(())
+    }
+
     #[test]
     fn test_parse_log_response_inner_events() -> Result<()> {
         use {
```
