# [?] Merge pull request #7011 from BowTiedRadone/fix/clarity-cli-panic

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-03-25
Source: https://github.com/stacks-network/stacks-core/commit/8b47a554a23f06806673eccc2b0d9e05f2d4caa2
Type: security-commit

## Details
Merge pull request #7011 from BowTiedRadone/fix/clarity-cli-panic

Update `clarity-cli` to print error and exit gracefully

## Patch
### changelog.d/7011-clarity-cli-graceful-errors.fixed
```diff
@@ -0,0 +1 @@
+Fixed `clarity-cli` to print errors to stderr and exit gracefully instead of panicking with a backtrace on invalid inputs.
\ No newline at end of file
```

### contrib/clarity-cli/src/lib.rs
```diff
@@ -102,14 +102,14 @@ macro_rules! panic_test {
     };
 }
 
-fn friendly_expect<A, B: std::fmt::Display>(input: Result<A, B>, msg: &str) -> A {
+pub fn friendly_expect<A, B: std::fmt::Display>(input: Result<A, B>, msg: &str) -> A {
     input.unwrap_or_else(|e| {
         eprintln!("{msg}\nCaused by: {e}");
         panic_test!();
     })
 }
 
-fn friendly_expect_opt<A>(input: Option<A>, msg: &str) -> A {
+pub fn friendly_expect_opt<A>(input: Option<A>, msg: &str) -> A {
     input.unwrap_or_else(|| {
         eprintln!("{msg}");
         panic_test!();
```

### contrib/clarity-cli/src/main.rs
```diff
@@ -23,16 +23,15 @@ use clarity::vm::{ClarityVersion, SymbolicExpression};
 use clarity_cli::{
     DEFAULT_CLI_EPOCH, execute_check, execute_eval, execute_eval_at_block,
     execute_eval_at_chaintip, execute_eval_raw, execute_execute, execute_generate_address,
-    execute_initialize, execute_launch, execute_repl, read_file_or_stdin,
-    read_optional_file_or_stdin, vm_execute_in_epoch,
+    execute_initialize, execute_launch, execute_repl, friendly_expect, friendly_expect_opt,
+    read_file_or_stdin, read_optional_file_or_stdin, vm_execute_in_epoch,
 };
 use stacks_common::types::StacksEpochId;
 
 /// Parse epoch string to StacksEpochId
 fn parse_epoch(epoch_str: Option<&String>) -> StacksEpochId {
     if let Some(s) = epoch_str {
-        s.parse::<StacksEpochId>()
-            .unwrap_or_else(|_| panic!("Invalid epoch: {s}"))
+        friendly_expect(s.parse::<StacksEpochId>(), &format!("Invalid epoch: {s}"))
     } else {
         DEFAULT_CLI_EPOCH
     }
@@ -41,8 +40,10 @@ fn parse_epoch(epoch_str: Option<&String>) -> StacksEpochId {
 /// Parse clarity_version string. Defaults to version for epoch if not specified.
 fn parse_clarity_version(cv_str: Option<&String>, epoch: StacksEpochId) -> ClarityVersion {
     if let Some(s) = cv_str {
-        s.parse::<ClarityVersion>()
-            .unwrap_or_else(|_| panic!("Invalid clarity version: {s}"))
+        friendly_expect(
+            s.parse::<ClarityVersion>(),
+            &format!("Invalid clarity version: {s}"),
+        )
     } else {
         ClarityVersion::default_for_epoch(epoch)
     }
@@ -52,7 +53,10 @@ fn parse_clarity_version(cv_str: Option<&String>, epoch: StacksEpochId) -> Clari
 fn parse_allocations(allocations_file: &Option<PathBuf>) -> Vec<(PrincipalData, u64)> {
     if let Some(filename) = allocations_file {
         let json_in = read_file_or_stdin(filename.to_str().expect("Invalid UTF-8 in path"));
-        clarity_cli::parse_allocations_json(&json_in).unwrap_or_else(|e| panic!("{e}"))
+        friendly_expect(
+            clarity_cli::parse_allocations_json(&json_in),
+            "Failed to parse allocations file",
+        )
     } else {
         vec![]
     }
@@ -397,9 +401,10 @@ fn main() {
             );
 
             let cid = if let Some(cid_str) = contract_id {
-                QualifiedContractIdentifier::parse(cid_str).unwrap_or_else(|e| {
-                    panic!("Error parsing contract identifier '{cid_str}': {e}")
-                })
+                friendly_expect(
+                    QualifiedContractIdentifier::parse(cid_str),
+                    &format!("Error parsing contract identifier '{cid_str}'"),
+                )
             } else {
                 QualifiedContractIdentifier::transient()
             };
@@ -458,8 +463,10 @@ fn main() {
             let epoch_id = parse_epoch(epoch.as_ref());
             let clarity_ver = parse_clarity_version(clarity_version.as_ref(), epoch_id);
 
-            let cid = QualifiedContractIdentifier::parse(contract_id)
-                .unwrap_or_else(|e| panic!("Failed to parse contract identifier: {e}"));
+            let cid = friendly_expect(
+                QualifiedContractIdentifier::parse(contract_id),
+                "Failed to parse contract identifier",
+            );
 
             let content = read_optional_file_or_stdin(program_file.as_ref());
 
@@ -479,8 +486,10 @@ fn main() {
             let epoch_id = parse_epoch(epoch.as_ref());
             let clarity_ver = parse_clarity_version(clarity_version.as_ref(), epoch_id);
 
-            let cid = QualifiedContractIdentifier::parse(contract_id)
-                .unwrap_or_else(|e| panic!("Failed to parse contract identifier: {e}"));
+            let cid = friendly_expect(
+                QualifiedContractIdentifier::parse(contract_id),
+                "Failed to parse contract identifier",
+            );
 
             let content = read_optional_file_or_stdin(program_file.as_ref());
 
@@ -501,8 +510,10 @@ fn main() {
             let epoch_id = parse_epoch(epoch.as_ref());
             let clarity_ver = parse_clarity_version(clarity_version.as_ref(), epoch_id);
 
-            let cid = QualifiedContractIdentifier::parse(contract_id)
-                .unwrap_or_else(|e| panic!("Failed to parse contract identifier: {e}"));
+            let cid = friendly_expect(
+                QualifiedContractIdentifier::parse(contract_id),
+                "Failed to parse contract identifier",
+            );
 
             let content = read_optional_file_or_stdin(program_file.as_ref());
 
@@ -532,8 +543,10 @@ fn main() {
             let epoch_id = parse_epoch(epoch.as_ref());
             let clarity_ver = parse_clarity_version(clarity_version.as_ref(), epoch_id);
 
-            let cid = QualifiedContractIdentifier::parse(contract_id)
-                .unwrap_or_else(|e| panic!("Failed to parse contract identifier: {e}"));
+            let cid = friendly_expect(
+                QualifiedContractIdentifier::parse(contract_id),
+                "Failed to parse contract identifier",
+            );
 
             let contract_src_file = contract_file
                 .to_str()
@@ -568,21 +581,27 @@ fn main() {
             let epoch_id = parse_epoch(epoch.as_ref());
             let clarity_ver = parse_clarity_version(clarity_version.as_ref(), epoch_id);
 
-            let cid = QualifiedContractIdentifier::parse(contract_id)
-                .unwrap_or_else(|e| panic!("Failed to parse contract identifier: {e}"));
+            let cid = friendly_expect(
+                QualifiedContractIdentifier::parse(contract_id),
+                "Failed to parse contract identifier",
+            );
 
-            let sender_principal = PrincipalData::parse_standard_principal(sender)
-                .map(PrincipalData::Standard)
-                .unwrap_or_else(|e| panic!("Unexpected result parsing sender {sender}: {e}"));
+            let sender_principal = PrincipalData::Standard(friendly_expect(
+                PrincipalData::parse_standard_principal(sender),
+                &format!("Unexpected result parsing sender {sender}"),
+            ));
 
             let arguments: Vec<_> = fn_args
                 .iter()
                 .map(|argument| {
-                    let argument_parsed = vm_execute_in_epoch(argument, clarity_ver, epoch_id)
-                        .unwrap_or_else(|e| panic!("Error parsing argument '{argument}': {e}"));
-                    let argument_value = argument_parsed.unwrap_or_else(|| {
-                        panic!("Failed to parse a value from the argument: {argument}")
-                    });
+                    let argument_parsed = friendly_expect(
+                        vm_execute_in_epoch(argument, clarity_ver, epoch_id),
+                        &format!("Error parsing argument '{argument}'"),
+                    );
+                    let argument_value = friendly_expect_opt(
+                        argument_parsed,
+                        &format!("Failed to parse a value from the argument '{argument}'"),
+                    );
                     SymbolicExpression::atom_value(argument_value)
                 })
                 .collect();
```
