# [?] client: Fix panic in event parsing due to empty stack (#2856)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2024-03-20
Source: https://github.com/otter-sec/anchor/commit/35142161deeaa5cbf37f2f5e56a45aa0f3932784
Type: security-commit

## Details
client: Fix panic in event parsing due to empty stack (#2856)

## Patch
### CHANGELOG.md
```diff
@@ -60,6 +60,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 - idl, ts: Make casing consistent ([#2824](https://github.com/coral-xyz/anchor/pull/2824)).
 - ts: Fix not being able to use numbers in instruction, account, or event names in some cases due to case conversion ([#2824](https://github.com/coral-xyz/anchor/pull/2824)).
 - cli: Fix excessive test validator requests ([#2828](https://github.com/coral-xyz/anchor/pull/2828)).
+- client: Fix `parse_logs_response` to prevent panics when more than 1 outer instruction exists in logs ([#2856](https://github.com/coral-xyz/anchor/pull/2856)).
 
 ### Breaking
 
```

### client/src/lib.rs
```diff
@@ -426,7 +426,10 @@ pub fn handle_program_log<T: anchor_lang::Event + anchor_lang::AnchorDeserialize
 pub fn handle_system_log(this_program_str: &str, log: &str) -> (Option<String>, bool) {
     if log.starts_with(&format!("Program {this_program_str} log:")) {
         (Some(this_program_str.to_string()), false)
-    } else if log.contains("invoke") {
+
+        // `Invoke [1]` instructions are pushed to the stack in `parse_logs_response`,
+        // so this ensures we only push CPIs to the stack at this stage
+    } else if log.contains("invoke") && !log.ends_with("[1]") {
         (Some("cpi".to_string()), false) // Any string will do.
     } else {
         let re = Regex::new(r"^Program (.*) success*$").unwrap();
@@ -681,7 +684,10 @@ fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
     let mut events: Vec<T> = Vec::new();
     if !logs.is_empty() {
         if let Ok(mut execution) = Execution::new(&mut logs) {
-            for l in logs {
+            // Create a new peekable iterator so that we can peek at the next log whilst iterating
+            let mut logs_iter = logs.iter().peekable();
+
+            while let Some(l) = logs_iter.next() {
                 // Parse the log.
                 let (event, new_program, did_pop) = {
                     if program_id_str == execution.program() {
@@ -705,6 +711,25 @@ fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
                 // Program returned.
                 if did_pop {
                     execution.pop();
+
+                    // If the current iteration popped then it means there was a
+                    //`Program x success` log. If the next log in the iteration is
+                    // of depth [1] then we're not within a CPI and this is a new instruction.
+                    //
+                    // We need to ensure that the `Execution` instance is updated with
+                    // the next program ID, or else `execution.program()` will cause
+                    // a panic during the next iteration.
+                    if let Some(&next_log) = logs_iter.peek() {
+                        if next_log.ends_with("invoke [1]") {
+                            let re = Regex::new(r"^Program (.*) invoke.*$").unwrap();
+                            let next_instruction =
+                                re.captures(next_log).unwrap().get(1).unwrap().as_str();
+                            // Within this if block, there will always be a regex match.
+                            // Therefore it's safe to unwrap and the captured program ID
+                            // at index 1 can also be safely unwrapped.
+                            execution.push(next_instruction.to_string());
+                        }
+                    };
                 }
             }
         }
@@ -714,6 +739,15 @@ fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
 
 #[cfg(test)]
 mod tests {
+    use solana_client::rpc_response::RpcResponseContext;
+
+    // Creating a mock struct that implements `anchor_lang::events`
+    // for type inference in `test_logs`
+    use anchor_lang::prelude::*;
+    #[derive(Debug, Clone, Copy)]
+    #[event]
+    pub struct MockEvent {}
+
     use super::*;
     #[test]
     fn new_execution() {
@@ -741,4 +775,106 @@ mod tests {
         assert_eq!(program, None);
         assert!(!did_pop);
     }
+
+    #[test]
+    fn test_parse_logs_response() -> Result<()> {
+        // Mock logs received within an `RpcResponse`. These are based on a Jupiter transaction.
+        let logs = vec![
+          "Program VeryCoolProgram invoke [1]", // Outer instruction #1 starts
+          "Program log: Instruction: VeryCoolEvent",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+          "Program log: Instruction: Transfer",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 664387 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program VeryCoolProgram consumed 42417 of 700000 compute units",
+          "Program VeryCoolProgram success", // Outer instruction #1 ends
+          "Program EvenCoolerProgram invoke [1]", // Outer instruction #2 starts
+          "Program log: Instruction: EvenCoolerEvent",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+          "Program log: Instruction: TransferChecked",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6200 of 630919 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program HyaB3W9q6XdA5xwpU4XnSZV94htfmbmqJXZcEbRaJutt invoke [2]",
+          "Program log: Instruction: Swap",
+          "Program log: INVARIANT: SWAP",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]",
+          "Program log: Instruction: Transfer",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 539321 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]",
+          "Program log: Instruction: Transfer",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 531933 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program HyaB3W9q6XdA5xwpU4XnSZV94htfmbmqJXZcEbRaJutt consumed 84670 of 610768 compute units",
+          "Program HyaB3W9q6XdA5xwpU4XnSZV94htfmbmqJXZcEbRaJutt success",
+          "Program EvenCoolerProgram invoke [2]",
+          "Program EvenCoolerProgram consumed 2021 of 523272 compute units",
+          "Program EvenCoolerProgram success",
+          "Program HyaB3W9q6XdA5xwpU4XnSZV94htfmbmqJXZcEbRaJutt invoke [2]",
+          "Program log: Instruction: Swap",
+          "Program log: INVARIANT: SWAP",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]",
+          "Program log: Instruction: Transfer",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 418618 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]",
+          "Program log: Instruction: Transfer",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 411230 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program HyaB3W9q6XdA5xwpU4XnSZV94htfmbmqJXZcEbRaJutt consumed 102212 of 507607 compute units",
+          "Program HyaB3W9q6XdA5xwpU4XnSZV94htfmbmqJXZcEbRaJutt success",
+          "Program EvenCoolerProgram invoke [2]",
+          "Program EvenCoolerProgram consumed 2021 of 402569 compute units",
+          "Program EvenCoolerProgram success",
+          "Program 9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP invoke [2]",
+          "Program log: Instruction: Swap",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]",
+          "Program log: Instruction: Transfer",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4736 of 371140 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]",
+          "Program log: Instruction: MintTo",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4492 of 341800 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]",
+          "Program log: Instruction: Transfer",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 334370 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program 9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP consumed 57610 of 386812 compute units",
+          "Program 9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP success",
+          "Program EvenCoolerProgram invoke [2]",
+          "Program EvenCoolerProgram consumed 2021 of 326438 compute units",
+          "Program EvenCoolerProgram success",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+          "Program log: Instruction: TransferChecked",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 6173 of 319725 compute units",
+          "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+          "Program EvenCoolerProgram consumed 345969 of 657583 compute units",
+          "Program EvenCoolerProgram success", // Outer instruction #2 ends
+          "Program ComputeBudget111111111111111111111111111111 invoke [1]",
+          "Program ComputeBudget111111111111111111111111111111 success",
+          "Program ComputeBudget111111111111111111111111111111 invoke [1]",
+          "Program ComputeBudget111111111111111111111111111111 success"];
+
+        // Converting to Vec<String> as expected in `RpcLogsResponse`
+        let logs: Vec<String> = logs.iter().map(|&l| l.to_string()).collect();
+
+        let program_id_str = "VeryCoolProgram";
+
+        // No events returned here. Just ensuring that the function doesn't panic
+        // due an incorrectly emptied stack.
+        let _: Vec<MockEvent> = parse_logs_response(
+            RpcResponse {
+                context: RpcResponseContext::new(0),
+                value: RpcLogsResponse {
+                    signature: "".to_string(),
+                    err: None,
+                    logs: logs.to_vec(),
+                },
+            },
+            program_id_str,
+        );
+
+        Ok(())
+    }
 }
```
