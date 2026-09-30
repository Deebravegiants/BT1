# [?] `forc-tx`: Improve error handling using `thiserror`. Fix `panic!`ing version/help output. (#4085)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2023-02-17
Source: https://github.com/FuelLabs/sway/commit/729f8b3bf8bb10d0e887946909515184bfd88fee
Type: security-commit

## Details
`forc-tx`: Improve error handling using `thiserror`. Fix `panic!`ing version/help output. (#4085)

## Description

This introduces a `Command::parse` constructor that emulates the
behaviour of the `clap` parse constructor in order to provide a more
consistent clap-like CLI experience. For context, we cannot use the
generated `parse` command due to limitations in clap's ability to handle
trailing subcommands as mentioned in #3804.

We switch to using `thiserror` in the library in order to allow for
handling error cases (necessary for the new `parse` constructor) and to
provide cleaner, more detailed error cause traces.

The help and version output no longer panic, and now behave like regular
clap applications. Closes #3886.

Also adds an example command invocation to the end of the `--help`
output.

## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [x] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

## Patch
### Cargo.lock
```diff
@@ -1764,6 +1764,7 @@ dependencies = [
  "fuel-tx",
  "serde",
  "serde_json",
+ "thiserror",
 ]
 
 [[package]]
```

### forc-plugins/forc-tx/Cargo.toml
```diff
@@ -22,3 +22,4 @@ devault = "0.1"
 fuel-tx = { workspace = true, features = ["serde"] }
 serde = "1.0"
 serde_json = { version = "1" }
+thiserror = "1"
```

### forc-plugins/forc-tx/src/lib.rs
```diff
@@ -1,14 +1,14 @@
 //! A simple tool for constructing transactions from the command line.
 
-use anyhow::{bail, Context};
 use clap::Parser;
 use devault::Devault;
 use serde::{Deserialize, Serialize};
 use std::path::PathBuf;
+use thiserror::Error;
 
 /// The top-level `forc tx` command.
 #[derive(Debug, Parser, Deserialize, Serialize)]
-#[clap(about, version)]
+#[clap(about, version, after_help = EXAMPLES)]
 pub struct Command {
     #[clap(long, short = 'o')]
     pub output_path: Option<PathBuf>,
@@ -306,29 +306,231 @@ pub struct OutputContractCreated {
     pub state_root: fuel_tx::Bytes32,
 }
 
+/// Errors that can occur while parsing the `Command`.
+#[derive(Debug, Error)]
+pub enum ParseError {
+    #[error("Failed to parse the command")]
+    Command {
+        #[source]
+        err: clap::Error,
+    },
+    #[error("Failed to parse transaction `input`")]
+    Input {
+        #[source]
+        err: clap::Error,
+    },
+    #[error("Failed to parse transaction `output`")]
+    Output {
+        #[source]
+        err: clap::Error,
+    },
+    #[error("Unrecognized argument {arg:?}, expected `input` or `output`")]
+    UnrecognizedArgumentExpectedInputOutput { arg: String, remaining: Vec<String> },
+    #[error("Found argument `input` which isn't valid for a mint transaction")]
+    MintTxHasInput,
+}
+
+/// Errors that can occur during conversion from the CLI transaction
+/// representation to the `fuel-tx` representation.
+#[derive(Debug, Error)]
+pub enum ConvertTxError {
+    #[error("failed to convert create transaction")]
+    Create(#[from] ConvertCreateTxError),
+    #[error("failed to convert script transaction")]
+    Script(#[from] ConvertScriptTxError),
+}
+
+/// Errors that can occur during "create" transaction conversion.
+#[derive(Debug, Error)]
+pub enum ConvertCreateTxError {
+    #[error("failed to open `--storage-slots` from {path:?}")]
+    StorageSlotsOpen {
+        path: PathBuf,
+        #[source]
+        err: std::io::Error,
+    },
+    #[error("failed to deserialize storage slots file")]
+    StorageSlotsDeserialize(#[source] serde_json::Error),
+    #[error("failed to convert an input")]
+    Input(#[from] ConvertInputError),
+}
+
+/// Errors that can occur during "script" transaction conversion.
+#[derive(Debug, Error)]
+pub enum ConvertScriptTxError {
+    #[error("failed to read `--bytecode` from {path:?}")]
+    BytecodeRead {
+        path: PathBuf,
+        #[source]
+        err: std::io::Error,
+    },
+    #[error("failed to read `--data` from {path:?}")]
+    DataRead {
+        path: PathBuf,
+        #[source]
+        err: std::io::Error,
+    },
+    #[error("failed to convert an input")]
+    Input(#[from] ConvertInputError),
+}
+
+/// Errors that can occur during transaction input conversion.
+#[derive(Debug, Error)]
+pub enum ConvertInputError {
+    #[error("failed to read `--msg-data` from {path:?}")]
+    MessageDataRead {
+        path: PathBuf,
+        #[source]
+        err: std::io::Error,
+    },
+    #[error("failed to read `--predicate` from {path:?}")]
+    PredicateRead {
+        path: PathBuf,
+        #[source]
+        err: std::io::Error,
+    },
+    #[error("failed to read `--predicate-data` from {path:?}")]
+    PredicateDataRead {
+        path: PathBuf,
+        #[source]
+        err: std::io::Error,
+    },
+    #[error("input accepts either witness index or predicate, not both")]
+    WitnessPredicateMismatch,
+}
+
+const EXAMPLES: &str = r#"EXAMPLES:
+    # An example constructing a `create` transaction.
+    forc tx create \
+        --bytecode ./my-contract/out/debug/my-contract.bin \
+        --storage-slots ./my-contract/out/debug/my-contract-storage_slots.json \
+        --gas-limit 100 \
+        --gas-price 0 \
+        --maturity 0 \
+        --witness ADFD \
+        --witness DFDA \
+        input coin \
+            --utxo-id 0 \
+            --output-ix 0 \
+            --owner 0x0000000000000000000000000000000000000000000000000000000000000000 \
+            --amount 100 \
+            --asset-id 0x0000000000000000000000000000000000000000000000000000000000000000 \
+            --tx-ptr 89ACBDEFBDEF \
+            --witness-ix 0 \
+            --maturity 0 \
+            --predicate ./my-predicate/out/debug/my-predicate.bin \
+            --predicate-data ./my-predicate.dat \
+        input contract \
+            --utxo-id 1 \
+            --output-ix 1 \
+            --balance-root 0x0000000000000000000000000000000000000000000000000000000000000000 \
+            --state-root 0x0000000000000000000000000000000000000000000000000000000000000000 \
+            --tx-ptr 89ACBDEFBDEF \
+            --contract-id 0xCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC \
+        input message \
+            --msg-id 0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB \
+            --sender 0x1111111111111111111111111111111111111111111111111111111111111111 \
+            --recipient 0x2222222222222222222222222222222222222222222222222222222222222222 \
+            --amount 1 \
+            --nonce 1234 \
+            --witness-ix 1 \
+            --msg-data ./message.dat \
+            --predicate ./my-predicate2/out/debug/my-predicate2.bin \
+            --predicate-data ./my-predicate2.dat \
+        output coin \
+            --to 0x2222222222222222222222222222222222222222222222222222222222222222 \
+            --amount 100 \
+            --asset-id 0x0000000000000000000000000000000000000000000000000000000000000000 \
+        output contract \
+            --input-ix 1 \
+            --balance-root 0x0000000000000000000000000000000000000000000000000000000000000000 \
+            --state-root 0x0000000000000000000000000000000000000000000000000000000000000000 \
+        output message \
+            --recipient 0x2222222222222222222222222222222222222222222222222222222222222222 \
+            --amount 100 \
+        output change \
+            --to 0x2222222222222222222222222222222222222222222222222222222222222222 \
+            --amount 100 \
+            --asset-id 0x0000000000000000000000000000000000000000000000000000000000000000 \
+        output variable \
+            --to 0x2222222222222222222222222222222222222222222222222222222222222222 \
+            --amount 100 \
+            --asset-id 0x0000000000000000000000000000000000000000000000000000000000000000 \
+        output contract-created \
+            --contract-id 0xCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC \
+            --state-root 0x0000000000000000000000000000000000000000000000000000000000000000
+"#;
+
+impl ParseError {
+    /// Print the error with clap's fancy formatting.
+    pub fn print(&self) -> Result<(), clap::Error> {
+        match self {
+            ParseError::Command { err } => {
+                err.print()?;
+            }
+            ParseError::Input { err } => {
+                err.print()?;
+            }
+            ParseError::Output { err } => {
+                err.print()?;
+            }
+            ParseError::UnrecognizedArgumentExpectedInputOutput { .. } => {
+                use clap::CommandFactory;
+                // Create a type as a hack to produce consistent-looking clap help output.
+                #[derive(Parser)]
+                enum ForcTxIo {
+                    #[clap(subcommand)]
+                    Input(Input),
+                    #[clap(subcommand)]
+                    Output(Output),
+                }
+                println!("{self}\n");
+                ForcTxIo::command().print_long_help()?;
+            }
+            ParseError::MintTxHasInput => {
+                println!("{self}");
+            }
+        }
+        Ok(())
+    }
+}
+
 impl Command {
+    /// Emulates `clap::Parser::parse` behaviour, but returns the parsed inputs and outputs.
+    ///
+    /// If parsing fails, prints the error along with the help output and exits with an error code.
+    ///
+    /// We provide this custom `parse` function solely due to clap's limitations around parsing
+    /// trailing subcommands.
+    pub fn parse() -> Self {
+        let err = match Self::try_parse() {
+            Err(err) => err,
+            Ok(cmd) => return cmd,
+        };
+        let _ = err.print();
+        std::process::exit(1);
+    }
+
     /// Parse a full `Transaction` including trailing inputs and outputs.
-    pub fn try_parse() -> anyhow::Result<Self> {
+    pub fn try_parse() -> Result<Self, ParseError> {
         Self::try_parse_from_args(std::env::args())
     }
 
     /// Parse a full `Transaction` including trailing inputs and outputs from an iterator yielding
     /// whitespace-separate string arguments.
-    pub fn try_parse_from_args(args: impl IntoIterator<Item = String>) -> anyhow::Result<Self> {
+    pub fn try_parse_from_args(args: impl IntoIterator<Item = String>) -> Result<Self, ParseError> {
         const INPUT: &str = "input";
         const OUTPUT: &str = "output";
 
         fn is_input_or_output(s: &str) -> bool {
             s == INPUT || s == OUTPUT
         }
 
-        fn push_input(cmd: &mut Transaction, input: Input) -> anyhow::Result<()> {
+        fn push_input(cmd: &mut Transaction, input: Input) -> Result<(), ParseError> {
             match cmd {
                 Transaction::Create(ref mut create) => create.inputs.push(input),
                 Transaction::Script(ref mut script) => script.inputs.push(input),
-                Transaction::Mint(_) => {
-                    bail!("Found argument 'input' which isn't valid for a Mint transaction");
-                }
+                Transaction::Mint(_) => return Err(ParseError::MintTxHasInput),
             }
             Ok(())
         }
@@ -346,7 +548,7 @@ impl Command {
         // Collect args until the first `input` or `output` is reached.
         let mut cmd = {
             let cmd_args = std::iter::from_fn(|| args.next_if(|s| !is_input_or_output(s)));
-            Command::try_parse_from(cmd_args)?
+            Command::try_parse_from(cmd_args).map_err(|err| ParseError::Command { err })?
         };
 
         // The remaining args (if any) are the inputs and outputs.
@@ -356,30 +558,38 @@ impl Command {
             }));
             match &arg[..] {
                 INPUT => {
-                    let input =
-                        Input::try_parse_from(args_til_next).context("failed to parse input")?;
+                    let input = Input::try_parse_from(args_til_next)
+                        .map_err(|err| ParseError::Input { err })?;
                     push_input(&mut cmd.tx, input)?
                 }
                 OUTPUT => {
-                    let output =
-                        Output::try_parse_from(args_til_next).context("failed to parse output")?;
+                    let output = Output::try_parse_from(args_til_next)
+                        .map_err(|err| ParseError::Output { err })?;
                     push_output(&mut cmd.tx, output)
                 }
-                arg => bail!("unexpected argument {arg}, expected 'input' or 'output'"),
+                arg => {
+                    return Err(ParseError::UnrecognizedArgumentExpectedInputOutput {
+                        arg: arg.to_string(),
+                        remaining: args.collect(),
+                    })
+                }
             }
         }
 
         // If there are args remaining, report them.
         if args.peek().is_some() {
-            bail!("Unexpected remaining args: {:?}", args.collect::<Vec<_>>());
+            return Err(ParseError::UnrecognizedArgumentExpectedInputOutput {
+                arg: args.peek().unwrap().to_string(),
+                remaining: args.collect(),
+            });
         }
 
         Ok(cmd)
     }
 }
 
 impl TryFrom<Transaction> for fuel_tx::Transaction {
-    type Error = anyhow::Error;
+    type Error = ConvertTxError;
     fn try_from(tx: Transaction) -> Result<Self, Self::Error> {
         let tx = match tx {
             Transaction::Create(create) => Self::Create(<_>::try_from(create)?),
@@ -391,12 +601,18 @@ impl TryFrom<Transaction> for fuel_tx::Transaction {
 }
 
 impl TryFrom<Create> for fuel_tx::Create {
-    type Error = anyhow::Error;
+    type Error = ConvertCreateTxError;
     fn try_from(create: Create) -> Result<Self, Self::Error> {
         let storage_slots = {
-            let file = std::fs::File::open(create.storage_slots)?;
+            let file = std::fs::File::open(&create.storage_slots).map_err(|err| {
+                ConvertCreateTxError::StorageSlotsOpen {
+                    path: create.storage_slots,
+                    err,
+                }
+            })?;
             let reader = std::io::BufReader::new(file);
-            serde_json::from_reader(reader).context("failed to parse storage_slots file")?
+            serde_json::from_reader(reader)
+                .map_err(ConvertCreateTxError::StorageSlotsDeserialize)?
         };
         let inputs = create
             .inputs
@@ -430,10 +646,19 @@ impl TryFrom<Create> for fuel_tx::Create {
 }
 
 impl TryFrom<Script> for fuel_tx::Script {
-    type Error = anyhow::Error;
+    type Error = ConvertScriptTxError;
     fn try_from(script: Script) -> Result<Self, Self::Error> {
-        let script_bytecode = std::fs::read(script.bytecode)?;
-        let script_data = std::fs::read(script.data)?;
+        let script_bytecode =
+            std::fs::read(&script.bytecode).map_err(|err| ConvertScriptTxError::BytecodeRead {
+                path: script.bytecode,
+                err,
+            })?;
+
+        let script_data =
+            std::fs::read(&script.data).map_err(|err| ConvertScriptTxError::DataRead {
+                path: script.data,
+                err,
+            })?;
         let inputs = script
             .inputs
             .into_iter()
@@ -476,7 +701,7 @@ impl From<Mint> for fuel_tx::Mint {
 }
 
 impl TryFrom<Input> for fuel_tx::Input {
-    type Error = anyhow::Error;
+    type Error = ConvertInputError;
     fn try_from(input: Input) -> Result<Self, Self::Error> {
         let input = match input {
             Input::Coin(coin) => {
@@ -510,11 +735,21 @@ impl TryFrom<Input> for fuel_tx::Input {
                             asset_id,
                             tx_pointer,
                             maturity: maturity as fuel_tx::Word,
-                            predicate: std::fs::read(predicate)?,
-                            predicate_data: std::fs::read(predicate_data)?,
+                            predicate: std::fs::read(&predicate).map_err(|err| {
+                                ConvertInputError::PredicateRead {
+                                    path: predicate,
+                                    err,
+                                }
+                            })?,
+                            predicate_data: std::fs::read(&predicate_data).map_err(|err| {
+                                ConvertInputError::PredicateDataRead {
+                                    path: predicate_data,
+                                    err,
+                                }
+                            })?,
                         }
                     }
-                    _ => bail!("input coin accepts either witness index or predicate, not both"),
+                    _ => return Err(ConvertInputError::WitnessPredicateMismatch),
                 }
             }
 
@@ -537,7 +772,11 @@ impl TryFrom<Input> for fuel_tx::Input {
                     witness_ix,
                     predicate,
                 } = msg;
-                let data = std::fs::read(msg_data)?;
+                let data =
+                    std::fs::read(&msg_data).map_err(|err| ConvertInputError::MessageDataRead {
+                        path: msg_data,
+                        err,
+                    })?;
                 match (witness_ix, predicate.bytecode, predicate.data) {
                     (Some(witness_index), None, None) => fuel_tx::Input::MessageSigned {
                         message_id,
@@ -556,11 +795,21 @@ impl TryFrom<Input> for fuel_tx::Input {
                             amount,
                             nonce,
                             data,
-                            predicate: std::fs::read(predicate)?,
-                            predicate_data: std::fs::read(predicate_data)?,
+                            predicate: std::fs::read(&predicate).map_err(|err| {
+                                ConvertInputError::PredicateRead {
+                                    path: predicate,
+                                    err,
+                                }
+                            })?,
+                            predicate_data: std::fs::read(&predicate_data).map_err(|err| {
+                                ConvertInputError::PredicateDataRead {
+                                    path: predicate_data,
+                                    err,
+                                }
+                            })?,
                         }
                     }
-                    _ => bail!("input message accepts either witness index or predicate, not both"),
+                    _ => return Err(ConvertInputError::WitnessPredicateMismatch),
                 }
             }
         };
```

### forc-plugins/forc-tx/src/main.rs
```diff
@@ -1,15 +1,16 @@
-fn main() {
-    let cmd = forc_tx::Command::try_parse().unwrap();
-    let tx = fuel_tx::Transaction::try_from(cmd.tx).unwrap();
+fn main() -> anyhow::Result<()> {
+    let cmd = forc_tx::Command::parse();
+    let tx = fuel_tx::Transaction::try_from(cmd.tx)?;
     match cmd.output_path {
         None => {
-            let string = serde_json::to_string_pretty(&tx).unwrap();
+            let string = serde_json::to_string_pretty(&tx)?;
             println!("{string}");
         }
         Some(path) => {
-            let file = std::fs::File::create(path).unwrap();
+            let file = std::fs::File::create(path)?;
             let writer = std::io::BufWriter::new(file);
-            serde_json::to_writer_pretty(writer, &tx).unwrap();
+            serde_json::to_writer_pretty(writer, &tx)?;
         }
     }
+    Ok(())
 }
```
