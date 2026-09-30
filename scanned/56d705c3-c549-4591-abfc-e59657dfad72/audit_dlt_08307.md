# [?] fix(client): avoid panic in parse_logs_response on stray "invoke [1]" suffix (#4475)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2026-05-08
Source: https://github.com/otter-sec/anchor/commit/9d853e156069d6c7ec20dc6fc387777a1d06ac50
Type: security-commit

## Details
fix(client): avoid panic in parse_logs_response on stray "invoke [1]" suffix (#4475)

## Patch
### CHANGELOG.md
```diff
@@ -23,6 +23,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 
 ### Fixes
 
+- client: Avoid panic in `parse_logs_response` when a program-emitted log line ends with `invoke [1]` ([#4461](https://github.com/solana-foundation/anchor/issues/4461)).
 - cli: Correctly honor `--skip-seed-phrase-validation` in `keygen recover` ([#4417](https://github.com/solana-foundation/anchor/pull/4417)).
 - spl: Fix wrong owner pubkey in CPI Guard enable/disable ([#4322](https://github.com/solana-foundation/anchor/pull/4322)).
 - ts: Fix `sha256.hash()` returning corrupted output by using hex encoding ([#4404](https://github.com/solana-foundation/anchor/pull/4404)).
```

### client/src/lib.rs
```diff
@@ -805,7 +805,7 @@ fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
         if let Ok(mut execution) = Execution::new(&mut logs) {
             // Create a new peekable iterator so that we can peek at the next log whilst iterating
             let mut logs_iter = logs.iter().peekable();
-            let regex = Regex::new(r"^Program ([1-9A-HJ-NP-Za-km-z]+) invoke \[[\d]+\]$").unwrap();
+            let regex = Regex::new(r"^Program ([1-9A-HJ-NP-Za-km-z]+) invoke \[(\d+)\]$").unwrap();
 
             while let Some(l) = logs_iter.next() {
                 // Parse the log.
@@ -836,14 +836,17 @@ fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
                     // We need to ensure that the `Execution` instance is updated with
                     // the next program ID, or else `execution.program()` will cause
                     // a panic during the next iteration.
+                    //
+                    // Use the full regex match to gate this branch. A loose
+                    // `ends_with("invoke [1]")` check would also accept program-emitted
+                    // log lines that happen to end in that suffix (e.g.
+                    // `"Program log: ...invoke [1]"`), which then fail the strict
+                    // `^Program <pubkey> invoke [N]$` regex and panic on unwrap.
                     if let Some(&next_log) = logs_iter.peek() {
-                        if next_log.ends_with("invoke [1]") {
-                            let next_instruction =
-                                regex.captures(next_log).unwrap().get(1).unwrap().as_str();
-                            // Within this if block, there will always be a regex match.
-                            // Therefore it's safe to unwrap and the captured program ID
-                            // at index 1 can also be safely unwrapped.
-                            execution.push(next_instruction.to_string());
+                        if let Some(caps) = regex.captures(next_log) {
+                            if &caps[2] == "1" {
+                                execution.push(caps[1].to_string());
+                            }
                         }
                     };
                 }
@@ -1047,6 +1050,40 @@ mod tests {
         Ok(())
     }
 
+    /// Regression for #4461: a program-emitted `Program log:` line that ends
+    /// with the literal `"invoke [1]"` (e.g. log content that happens to
+    /// describe a CPI) used to satisfy the `ends_with` gate but fail the
+    /// strict `^Program <pubkey> invoke [N]$` regex, panicking on
+    /// `.captures(...).unwrap()` whenever it appeared right after a CPI pop.
+    #[test]
+    fn test_parse_logs_response_log_line_ends_with_invoke_1() -> Result<()> {
+        let logs = [
+            "Program VeryCoolProgram invoke [1]",
+            "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+            "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+            // Program-emitted log that happens to end with "invoke [1]"
+            // immediately after a CPI returns. Pre-fix this would panic.
+            "Program log: forwarded inner instruction invoke [1]",
+            "Program VeryCoolProgram success",
+        ];
+        let logs: Vec<String> = logs.iter().map(|&l| l.to_string()).collect();
+
+        parse_logs_response::<MockEvent>(
+            RpcResponse {
+                context: RpcResponseContext::new(0),
+                value: RpcLogsResponse {
+                    signature: "".to_string(),
+                    err: None,
+                    logs,
+                },
+            },
+            "VeryCoolProgram",
+        )
+        .unwrap();
+
+        Ok(())
+    }
+
     /// Regression test that registering multiple event listeners does not deadlock.
     #[test]
     fn multiple_listeners_no_deadlock() {
```
