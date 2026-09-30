# [?] Removing non-determinism in R1CS generation: fixing assignment order of anonymous components inputs

## Summary
Severity: Unknown
Chain: ZK
Component: iden3/circom
Published: 2024-01-07
Source: https://github.com/iden3/circom/commit/6ef8f179c719217d00fed55474fc4a9e1a58844b
Type: security-commit

## Details
Removing non-determinism in R1CS generation: fixing assignment order of anonymous components inputs

## Patch
### Cargo.lock
```diff
@@ -105,7 +105,7 @@ checksum = "baf1de4339761588bc0619e3cbc0120ee582ebb74b53b4efbf79117bd2da40fd"
 
 [[package]]
 name = "circom"
-version = "2.1.6"
+version = "2.1.7"
 dependencies = [
  "ansi_term",
  "clap",
@@ -146,7 +146,7 @@ dependencies = [
 
 [[package]]
 name = "code_producers"
-version = "2.1.6"
+version = "2.1.7"
 dependencies = [
  "handlebars",
  "lz_fnv",
@@ -175,7 +175,7 @@ dependencies = [
 
 [[package]]
 name = "compiler"
-version = "2.1.6"
+version = "2.1.7"
 dependencies = [
  "code_producers",
  "constant_tracking",
@@ -190,7 +190,7 @@ version = "2.0.0"
 
 [[package]]
 name = "constraint_generation"
-version = "2.1.6"
+version = "2.1.7"
 dependencies = [
  "ansi_term",
  "circom_algebra",
@@ -205,7 +205,7 @@ dependencies = [
 
 [[package]]
 name = "constraint_list"
-version = "2.1.5"
+version = "2.1.7"
 dependencies = [
  "circom_algebra",
  "constraint_writers",
@@ -217,7 +217,7 @@ dependencies = [
 
 [[package]]
 name = "constraint_writers"
-version = "2.1.5"
+version = "2.1.7"
 dependencies = [
  "circom_algebra",
  "json",
@@ -250,7 +250,7 @@ dependencies = [
 
 [[package]]
 name = "dag"
-version = "2.1.5"
+version = "2.1.7"
 dependencies = [
  "circom_algebra",
  "constraint_list",
@@ -655,7 +655,7 @@ dependencies = [
 
 [[package]]
 name = "parser"
-version = "2.1.6"
+version = "2.1.7"
 dependencies = [
  "lalrpop",
  "lalrpop-util",
@@ -754,7 +754,7 @@ dependencies = [
 
 [[package]]
 name = "program_structure"
-version = "2.1.6"
+version = "2.1.7"
 dependencies = [
  "codespan",
  "codespan-reporting",
@@ -1047,7 +1047,7 @@ dependencies = [
 
 [[package]]
 name = "type_analysis"
-version = "2.1.5"
+version = "2.1.7"
 dependencies = [
  "num-bigint-dig",
  "num-traits",
```

### parser/src/syntax_sugar_remover.rs
```diff
@@ -6,7 +6,7 @@ use program_structure::file_definition::FileLibrary;
 use program_structure::program_archive::ProgramArchive;
 use program_structure::statement_builders::{build_declaration, build_log_call, build_initialization_block};
 use program_structure::template_data::TemplateData;
-use std::collections::HashMap;
+use std::collections::{HashMap, BTreeMap};
 use num_bigint::BigInt;
 
 
@@ -469,7 +469,7 @@ pub fn remove_anonymous_from_expression(
 
             // assign the inputs
             // reorder the signals in new_signals (case names)
-            let mut inputs_to_assignments = HashMap::new();
+            let mut inputs_to_assignments = BTreeMap::new();
 
             if let Some(m) = names { // in case we have a list of names and assignments
                 let inputs = template.unwrap().get_inputs();
```
