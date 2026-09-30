# [?] fix(hardfork): `ckb init` will panic when specifies arguments for "block_assembler"

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-06-17
Source: https://github.com/nervosnetwork/ckb/commit/af792f2f766cc49ff24cb7aad5e0eb4e21955239
Type: security-commit

## Details
fix(hardfork): `ckb init` will panic when specifies arguments for "block_assembler"

## Patch
### ckb-bin/src/subcommand/init.rs
```diff
@@ -4,7 +4,7 @@ use std::io::{self, Read};
 use crate::helper::prompt;
 use ckb_app_config::{cli, AppConfig, ExitCode, InitArgs};
 use ckb_chain_spec::ChainSpec;
-use ckb_jsonrpc_types::ScriptHashType;
+use ckb_jsonrpc_types::{ScriptHashTypeShadow, VmVersion};
 use ckb_resource::{
     Resource, TemplateContext, AVAILABLE_SPECS, CKB_CONFIG_FILE_NAME, DB_OPTIONS_FILE_NAME,
     MINER_CONFIG_FILE_NAME, SPEC_DEV_FILE_NAME,
@@ -48,7 +48,6 @@ pub fn init(args: InitArgs) -> Result<(), ExitCode> {
         let in_block_assembler_code_hash = prompt("code hash: ");
         let in_args = prompt("args: ");
         let in_hash_type = prompt("hash_type: ");
-        let in_message = prompt("message: ");
 
         args.block_assembler_code_hash = Some(in_block_assembler_code_hash.trim().to_string());
 
@@ -58,12 +57,21 @@ pub fn init(args: InitArgs) -> Result<(), ExitCode> {
             .map(|s| s.to_string())
             .collect::<Vec<String>>();
 
-        args.block_assembler_message = Some(in_message.trim().to_string());
-
-        match serde_plain::from_str::<ScriptHashType>(in_hash_type.trim()).ok() {
+        match serde_plain::from_str::<ScriptHashTypeShadow>(in_hash_type.trim()).ok() {
             Some(hash_type) => args.block_assembler_hash_type = hash_type,
             None => eprintln!("Invalid block assembler hash type"),
         }
+
+        if args.block_assembler_hash_type == ScriptHashTypeShadow::Type {
+            let in_vm_version = prompt("vm_version: ");
+            match serde_plain::from_str::<VmVersion>(in_vm_version.trim()).ok() {
+                Some(vm_version) => args.block_assembler_vm_version = Some(vm_version),
+                None => eprintln!("Invalid block assembler vm version"),
+            }
+        }
+
+        let in_message = prompt("message: ");
+        args.block_assembler_message = Some(in_message.trim().to_string());
     }
 
     // Try to find the default secp256k1 from bundled chain spec.
@@ -90,7 +98,7 @@ pub fn init(args: InitArgs) -> Result<(), ExitCode> {
     let block_assembler = match block_assembler_code_hash {
         Some(hash) => {
             if let Some(default_code_hash) = &default_code_hash_option {
-                if ScriptHashType::Type != args.block_assembler_hash_type {
+                if ScriptHashTypeShadow::Type != args.block_assembler_hash_type {
                     eprintln!(
                         "WARN: the default lock should use hash type `{}`, you are using `{}`.\n\
                          It will require `ckb run --ba-advanced` to enable this block assembler",
@@ -111,18 +119,35 @@ pub fn init(args: InitArgs) -> Result<(), ExitCode> {
                     );
                 }
             }
-            format!(
-                "[block_assembler]\n\
-                 code_hash = \"{}\"\n\
-                 args = \"{}\"\n\
-                 hash_type = \"{}\"\n\
-                 message = \"{}\"",
-                hash,
-                args.block_assembler_args.join("\", \""),
-                serde_plain::to_string(&args.block_assembler_hash_type).unwrap(),
-                args.block_assembler_message
-                    .unwrap_or_else(|| "0x".to_string()),
-            )
+            if let Some(default_vm_version) = &args.block_assembler_vm_version {
+                format!(
+                    "[block_assembler]\n\
+                    code_hash = \"{}\"\n\
+                    args = \"{}\"\n\
+                    hash_type = \"{}\"\n\
+                    vm_version = \"{}\"\n\
+                    message = \"{}\"",
+                    hash,
+                    args.block_assembler_args.join("\", \""),
+                    args.block_assembler_hash_type,
+                    serde_plain::to_string(&default_vm_version).unwrap(),
+                    args.block_assembler_message
+                        .unwrap_or_else(|| "0x".to_string()),
+                )
+            } else {
+                format!(
+                    "[block_assembler]\n\
+                    code_hash = \"{}\"\n\
+                    args = \"{}\"\n\
+                    hash_type = \"{}\"\n\
+                    message = \"{}\"",
+                    hash,
+                    args.block_assembler_args.join("\", \""),
+                    args.block_assembler_hash_type,
+                    args.block_assembler_message
+                        .unwrap_or_else(|| "0x".to_string()),
+                )
+            }
         }
         None => {
             eprintln!("WARN: mining feature is disabled because of lacking the block assembler config options");
```

### util/app-config/src/args.rs
```diff
@@ -1,6 +1,6 @@
 use crate::{CKBAppConfig, MemoryTrackerConfig, MinerConfig};
 use ckb_chain_spec::consensus::Consensus;
-use ckb_jsonrpc_types::ScriptHashType;
+use ckb_jsonrpc_types::{ScriptHashTypeShadow, VmVersion};
 use ckb_pow::PowEngine;
 use ckb_types::packed::Byte32;
 use faketime::unix_time_as_millis;
@@ -114,7 +114,9 @@ pub struct InitArgs {
     /// Block assembler lock script args.
     pub block_assembler_args: Vec<String>,
     /// Block assembler lock script hash type.
-    pub block_assembler_hash_type: ScriptHashType,
+    pub block_assembler_hash_type: ScriptHashTypeShadow,
+    /// Block assembler lock script vm version when hash type is "data".
+    pub block_assembler_vm_version: Option<VmVersion>,
     /// Block assembler cellbase transaction message.
     pub block_assembler_message: Option<String>,
     /// Import the spec file.
```

### util/app-config/src/cli.rs
```diff
@@ -68,6 +68,8 @@ pub const ARG_BA_CODE_HASH: &str = "ba-code-hash";
 pub const ARG_BA_ARG: &str = "ba-arg";
 /// Command line argument `--ba-hash-type`.
 pub const ARG_BA_HASH_TYPE: &str = "ba-hash-type";
+/// Command line argument `--ba-vm-version`.
+pub const ARG_BA_VM_VERSION: &str = "ba-vm-version";
 /// Command line argument `--ba-message`.
 pub const ARG_BA_MESSAGE: &str = "ba-message";
 /// Command line argument `--ba-advanced`.
@@ -450,6 +452,13 @@ fn init() -> App<'static, 'static> {
                 .default_value("type")
                 .help("Sets hash type in [block_assembler]"),
         )
+        .arg(
+            Arg::with_name(ARG_BA_VM_VERSION)
+                .long(ARG_BA_VM_VERSION)
+                .value_name("vm_version")
+                .takes_value(true)
+                .help("Sets vm version for data hash-type script in [block_assembler]"),
+        )
         .group(
             ArgGroup::with_name(GROUP_BA)
                 .args(&[ARG_BA_CODE_HASH, ARG_BA_ARG])
```

### util/app-config/src/lib.rs
```diff
@@ -16,7 +16,7 @@ pub use configs::*;
 pub use exit_code::ExitCode;
 
 use ckb_chain_spec::{consensus::Consensus, ChainSpec};
-use ckb_jsonrpc_types::ScriptHashType;
+use ckb_jsonrpc_types::{ScriptHashTypeShadow, VmVersion};
 use ckb_types::{u256, H256, U256};
 use clap::{value_t, ArgMatches, ErrorKind};
 use std::{path::PathBuf, str::FromStr};
@@ -246,7 +246,12 @@ impl Setup {
             .collect();
         let block_assembler_hash_type = matches
             .value_of(cli::ARG_BA_HASH_TYPE)
-            .and_then(|hash_type| serde_plain::from_str::<ScriptHashType>(hash_type).ok())
+            .and_then(|hash_type| serde_plain::from_str::<ScriptHashTypeShadow>(hash_type).ok())
+            .unwrap();
+        let block_assembler_vm_version = matches
+            .value_of(cli::ARG_BA_VM_VERSION)
+            .map(|vm_version| serde_plain::from_str::<VmVersion>(vm_version))
+            .transpose()
             .unwrap();
         let block_assembler_message = matches.value_of(cli::ARG_BA_MESSAGE).map(str::to_string);
 
@@ -272,6 +277,7 @@ impl Setup {
             block_assembler_code_hash,
             block_assembler_args,
             block_assembler_hash_type,
+            block_assembler_vm_version,
             block_assembler_message,
             import_spec,
             customize_spec,
```

### util/jsonrpc-types/src/blockchain.rs
```diff
@@ -29,7 +29,7 @@ pub enum ScriptHashType {
 }
 
 #[doc(hidden)]
-#[derive(Deserialize)]
+#[derive(Clone, Copy, Deserialize, PartialEq, Eq, Hash, Debug)]
 #[serde(rename_all = "snake_case")]
 pub enum ScriptHashTypeShadow {
     Data,
@@ -75,6 +75,15 @@ impl fmt::Display for ScriptHashType {
     }
 }
 
+impl fmt::Display for ScriptHashTypeShadow {
+    fn fmt(&self, f: &mut fmt::Formatter) -> Result<(), fmt::Error> {
+        match self {
+            ScriptHashTypeShadow::Data => write!(f, "data"),
+            ScriptHashTypeShadow::Type => write!(f, "type"),
+        }
+    }
+}
+
 /// Describes the lock script and type script for a cell.
 ///
 /// ## Examples
```
