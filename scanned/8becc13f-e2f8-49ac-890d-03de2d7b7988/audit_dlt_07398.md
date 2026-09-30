# [?] fix(cast): split subcommands to avoid stack overflow (#17079)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-26
Source: https://github.com/foundry-rs/foundry/commit/336712cd92aa584504891fd2e6628e602ca28ae5
Type: security-commit

## Details
fix(cast): split subcommands to avoid stack overflow (#17079)

* fix(cast): split subcommands to avoid stack overflow

clap's derive expands every `CastSubcommand` variant, including the
inline args of struct variants, into a single `augment_subcommands`
function. Without optimizations each intermediate `Command` (712 bytes)
and `Arg` (640 bytes) gets its own stack slot, so that function had a
2,080,480 byte frame in debug builds, more than the 2 MiB stack of test
threads. The `opts::tests` parse tests aborted locally and only passed
in CI because it sets RUST_MIN_STACK.

Group the variants into flattened enums that follow the sections in
`run_command`. The CLI is unchanged and the largest generated frame is
now 696,800 bytes.

* Delete cast-debug-cli-stack-overflow.md

---------

Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>

## Patch
### crates/cast/src/args.rs
```diff
@@ -1,7 +1,10 @@
 use crate::{
     base::{Base, NumberWithBase},
     cmd::{erc20::IERC20, rpc_provider},
-    opts::{Cast as CastArgs, CastSubcommand, ToBaseArgs},
+    opts::{
+        AbiSubcommand, Cast as CastArgs, CastSubcommand, ConversionSubcommand, MiscSubcommand,
+        QuerySubcommand, ToBaseArgs, TransactionSubcommand,
+    },
     traces::identifier::SignaturesIdentifier,
     tx::CastTxSender,
 };
@@ -126,31 +129,39 @@ pub fn setup() -> Result<()> {
 pub async fn run_command(args: CastArgs) -> Result<()> {
     match args.cmd {
         // Constants
-        CastSubcommand::MaxInt { r#type } | CastSubcommand::MaxUint { r#type } => {
+        CastSubcommand::Conversion(
+            ConversionSubcommand::MaxInt { r#type } | ConversionSubcommand::MaxUint { r#type },
+        ) => {
             print_scalar(int_bound(&r#type, true)?)?;
         }
-        CastSubcommand::MinInt { r#type } => print_scalar(int_bound(&r#type, false)?)?,
-        CastSubcommand::AddressZero => print_scalar(format!("{:?}", Address::ZERO))?,
-        CastSubcommand::HashZero => print_scalar(format!("{:?}", B256::ZERO))?,
+        CastSubcommand::Conversion(ConversionSubcommand::MinInt { r#type }) => {
+            print_scalar(int_bound(&r#type, false)?)?
+        }
+        CastSubcommand::Conversion(ConversionSubcommand::AddressZero) => {
+            print_scalar(format!("{:?}", Address::ZERO))?
+        }
+        CastSubcommand::Conversion(ConversionSubcommand::HashZero) => {
+            print_scalar(format!("{:?}", B256::ZERO))?
+        }
 
         // Conversions & transformations
-        CastSubcommand::FromUtf8 { text } => {
+        CastSubcommand::Conversion(ConversionSubcommand::FromUtf8 { text }) => {
             print_scalar(hex::encode_prefixed(stdin::unwrap(text, false)?))?;
         }
-        CastSubcommand::ToAscii { hexdata } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToAscii { hexdata }) => {
             let bytes = hex::decode(stdin::unwrap(hexdata, false)?.trim())?;
             eyre::ensure!(bytes.iter().all(u8::is_ascii), "Invalid ASCII bytes");
             print_scalar(String::from_utf8(bytes).unwrap())?;
         }
-        CastSubcommand::ToUtf8 { hexdata } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToUtf8 { hexdata }) => {
             let bytes = hex::decode(stdin::unwrap(hexdata, false)?)?;
             print_scalar(String::from_utf8_lossy(&bytes).into_owned())?;
         }
-        CastSubcommand::FromFixedPoint { value, decimals } => {
+        CastSubcommand::Conversion(ConversionSubcommand::FromFixedPoint { value, decimals }) => {
             let (value, decimals) = stdin::unwrap2(value, decimals)?;
             print_scalar(ParseUnits::parse_units(&value, Unit::from_str(&decimals)?)?.to_string())?;
         }
-        CastSubcommand::ToFixedPoint { value, decimals } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToFixedPoint { value, decimals }) => {
             let (value, decimals) = stdin::unwrap2(value, decimals)?;
 
             let number = NumberWithBase::parse_int(&value, None)?;
@@ -171,7 +182,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             }
             print_scalar(format!("{sign}{value}"))?;
         }
-        CastSubcommand::ConcatHex { data } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ConcatHex { data }) => {
             let input;
             let values = if data.is_empty() {
                 input = stdin::read(true)?;
@@ -182,10 +193,10 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             let out = values.map(strip_0x).collect::<String>();
             print_scalar(format!("0x{out}"))?;
         }
-        CastSubcommand::FromBin => {
+        CastSubcommand::Conversion(ConversionSubcommand::FromBin) => {
             print_scalar(hex::encode_prefixed(stdin::read_bytes(false)?))?;
         }
-        CastSubcommand::ToHexdata { input } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToHexdata { input }) => {
             let value = stdin::unwrap_line(input)?;
             let output = match value {
                 s if s.starts_with('@') => hex::encode(std::env::var(&s[1..])?),
@@ -194,18 +205,21 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_scalar(format!("0x{output}"))?;
         }
-        CastSubcommand::ToCheckSumAddress { address, chain_id } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToCheckSumAddress {
+            address,
+            chain_id,
+        }) => {
             print_scalar(stdin::unwrap_line(address)?.to_checksum(chain_id))?;
         }
-        CastSubcommand::ToUint256 { value } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToUint256 { value }) => {
             let n = NumberWithBase::parse_uint(&stdin::unwrap_line(value)?, None)?;
             print_scalar(format!("{n:#066x}"))?;
         }
-        CastSubcommand::ToInt256 { value } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToInt256 { value }) => {
             let n = NumberWithBase::parse_int(&stdin::unwrap_line(value)?, None)?;
             print_scalar(format!("{n:#066x}"))?;
         }
-        CastSubcommand::ToUnit { value, unit } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToUnit { value, unit }) => {
             let value = stdin::unwrap_line(value)?;
             let value = DynSolType::coerce_str(&DynSolType::Uint(256), &value)?
                 .as_uint()
@@ -214,27 +228,27 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             let unit = unit.parse().wrap_err("could not parse units")?;
             print_scalar(format_unit_as_string(ParseUnits::U256(value), unit))?;
         }
-        CastSubcommand::ParseUnits { value, unit } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ParseUnits { value, unit }) => {
             let value = stdin::unwrap_line(value)?;
             let unit = Unit::new(unit).ok_or_else(|| eyre::eyre!("invalid unit"))?;
 
             print_scalar(ParseUnits::parse_units(&value, unit)?.to_string())?;
         }
-        CastSubcommand::FormatUnits { value, unit } => {
+        CastSubcommand::Conversion(ConversionSubcommand::FormatUnits { value, unit }) => {
             print_scalar(format_units(&stdin::unwrap_line(value)?, unit)?)?;
         }
-        CastSubcommand::FromWei { value, unit } => {
+        CastSubcommand::Conversion(ConversionSubcommand::FromWei { value, unit }) => {
             print_scalar(
                 signed_parse_units(&NumberWithBase::parse_int(&stdin::unwrap_line(value)?, None)?)?
                     .format_units(unit.parse()?),
             )?;
         }
-        CastSubcommand::ToWei { value, unit } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToWei { value, unit }) => {
             let value = stdin::unwrap_line(value)?;
             let unit = unit.parse().wrap_err("could not parse units")?;
             print_scalar(ParseUnits::parse_units(&value, unit)?.to_string())?;
         }
-        CastSubcommand::FromRlp { value, as_int } => {
+        CastSubcommand::Conversion(ConversionSubcommand::FromRlp { value, as_int }) => {
             let bytes = hex::decode(stdin::unwrap_line(value)?).wrap_err("Could not decode hex")?;
             let value = if as_int {
                 U256::decode(&mut &bytes[..])?.to_string()
@@ -245,26 +259,29 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_scalar(value)?;
         }
-        CastSubcommand::ToRlp { value } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToRlp { value }) => {
             let value = stdin::unwrap_line(value)?;
             let val =
                 serde_json::from_str(&value).unwrap_or_else(|_| serde_json::Value::String(value));
             let item = crate::rlp_converter::Item::value_to_item(&val)?;
             print_scalar(format!("0x{}", hex::encode(alloy_rlp::encode(item))))?;
         }
-        CastSubcommand::ToHex(ToBaseArgs { value, base_in }) => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToHex(ToBaseArgs { value, base_in })) => {
             let value = stdin::unwrap_line(value)?;
             print_scalar(to_base(&value, base_in.as_deref(), "hex")?)?;
         }
-        CastSubcommand::ToDec(ToBaseArgs { value, base_in }) => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToDec(ToBaseArgs { value, base_in })) => {
             let value = stdin::unwrap_line(value)?;
             print_scalar(to_base(&value, base_in.as_deref(), "dec")?)?;
         }
-        CastSubcommand::ToBase { base: ToBaseArgs { value, base_in }, base_out } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToBase {
+            base: ToBaseArgs { value, base_in },
+            base_out,
+        }) => {
             let (value, base_out) = stdin::unwrap2(value, base_out)?;
             print_scalar(to_base(&value, base_in.as_deref(), &base_out)?)?;
         }
-        CastSubcommand::ToBytes32 { bytes } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToBytes32 { bytes }) => {
             let s = stdin::unwrap_line(bytes)?;
             let s = strip_0x(&s);
             if s.len() > 64 {
@@ -274,7 +291,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             let padded = format!("{s:0<64}");
             print_scalar(padded.parse::<B256>()?.to_string())?;
         }
-        CastSubcommand::ToBytesMemory { data } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ToBytesMemory { data }) => {
             let data = stdin::unwrap_line(data)?;
             const WORD: usize = 32;
 
@@ -286,7 +303,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             out.resize(WORD + padded_len, 0);
             print_scalar(hex::encode_prefixed(out))?;
         }
-        CastSubcommand::Pad { data, right, left: _, len } => {
+        CastSubcommand::Conversion(ConversionSubcommand::Pad { data, right, left: _, len }) => {
             let s = stdin::unwrap_line(data)?;
             let s = strip_0x(&s);
             let hex_len = len
@@ -308,7 +325,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 format!("0x{s:0>hex_len$}")
             })?;
         }
-        CastSubcommand::FormatBytes32String { string } => {
+        CastSubcommand::Conversion(ConversionSubcommand::FormatBytes32String { string }) => {
             let s = stdin::unwrap_line(string)?;
             let str_bytes: &[u8] = s.as_bytes();
             eyre::ensure!(
@@ -320,14 +337,14 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             bytes32[..str_bytes.len()].copy_from_slice(str_bytes);
             print_scalar(hex::encode_prefixed(bytes32))?;
         }
-        CastSubcommand::ParseBytes32String { bytes } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ParseBytes32String { bytes }) => {
             let s = stdin::unwrap_line(bytes)?;
             let bytes = hex::decode(s)?;
             eyre::ensure!(bytes.len() == 32, "expected 32 byte hex-string");
             let len = bytes.iter().take_while(|x| **x != 0).count();
             print_scalar(std::str::from_utf8(&bytes[..len])?)?;
         }
-        CastSubcommand::ParseBytes32Address { bytes } => {
+        CastSubcommand::Conversion(ConversionSubcommand::ParseBytes32Address { bytes }) => {
             let s = stdin::unwrap_line(bytes)?;
             let s = strip_0x(&s);
             if s.len() != 64 {
@@ -340,10 +357,10 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
         }
 
         // ABI encoding & decoding
-        CastSubcommand::DecodeAbi { sig, calldata, input } => {
+        CastSubcommand::Abi(AbiSubcommand::DecodeAbi { sig, calldata, input }) => {
             print_tokens(&abi_decode_calldata(&sig, &calldata, input, false)?)?;
         }
-        CastSubcommand::AbiEncode { sig, packed, args } => {
+        CastSubcommand::Abi(AbiSubcommand::AbiEncode { sig, packed, args }) => {
             let out = if packed {
                 // If the signature is a tuple, we need to prefix it to make it a function
                 let sig = if sig.trim_start().starts_with('(') { format!("foo{sig}") } else { sig };
@@ -364,7 +381,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
         }
         // TODO(json): multi-line output (one line per topic + data field), needs structured object
         // envelope
-        CastSubcommand::AbiEncodeEvent { sig, args } => {
+        CastSubcommand::Abi(AbiSubcommand::AbiEncodeEvent { sig, args }) => {
             let event = get_event(&sig)?;
             if event.inputs.len() != args.len() {
                 eyre::bail!(
@@ -415,14 +432,14 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 }
             }
         }
-        CastSubcommand::DecodeCalldata { sig, calldata, file } => {
+        CastSubcommand::Abi(AbiSubcommand::DecodeCalldata { sig, calldata, file }) => {
             let raw_hex = match file {
                 Some(file_path) => fs::read_to_string(&file_path)?.trim().to_string(),
                 None => calldata.unwrap(),
             };
             print_tokens(&abi_decode_calldata(&sig, &raw_hex, true, true)?)?;
         }
-        CastSubcommand::CalldataEncode { sig, args, file } => {
+        CastSubcommand::Abi(AbiSubcommand::CalldataEncode { sig, args, file }) => {
             let args = match file {
                 Some(file_path) => fs::read_to_string(file_path)?
                     .lines()
@@ -434,10 +451,10 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_scalar(hex::encode_prefixed(encode_function_args(&get_func(&sig)?, &args)?))?;
         }
-        CastSubcommand::DecodeString { data } => {
+        CastSubcommand::Abi(AbiSubcommand::DecodeString { data }) => {
             print_tokens(&abi_decode_calldata("Any(string)", &data, true, true)?)?;
         }
-        CastSubcommand::DecodeEvent { sig, data } => {
+        CastSubcommand::Abi(AbiSubcommand::DecodeEvent { sig, data }) => {
             let decoded_values = if let Some(event_sig) = sig {
                 let event = get_event(&event_sig)?;
                 abi_decode_event_data(&event, &hex::decode(data)?)?
@@ -456,7 +473,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_tokens(&decoded_values)?;
         }
-        CastSubcommand::DecodeError { sig, data } => {
+        CastSubcommand::Abi(AbiSubcommand::DecodeError { sig, data }) => {
             let error = if let Some(err_sig) = sig {
                 get_error(&err_sig)?
             } else {
@@ -472,18 +489,18 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_tokens(&error.decode_error(&hex::decode(data)?)?.body)?;
         }
-        CastSubcommand::Interface(cmd) => cmd.run().await?,
-        CastSubcommand::CreationCode(cmd) => cmd.run().await?,
-        CastSubcommand::ConstructorArgs(cmd) => cmd.run().await?,
-        CastSubcommand::Artifact(cmd) => cmd.run().await?,
-        CastSubcommand::Bind(cmd) => cmd.run().await?,
-        CastSubcommand::B2EPayload(cmd) => cmd.run().await?,
-        CastSubcommand::PrettyCalldata { calldata, offline } => {
+        CastSubcommand::Abi(AbiSubcommand::Interface(cmd)) => cmd.run().await?,
+        CastSubcommand::Abi(AbiSubcommand::CreationCode(cmd)) => cmd.run().await?,
+        CastSubcommand::Abi(AbiSubcommand::ConstructorArgs(cmd)) => cmd.run().await?,
+        CastSubcommand::Abi(AbiSubcommand::Artifact(cmd)) => cmd.run().await?,
+        CastSubcommand::Abi(AbiSubcommand::Bind(cmd)) => cmd.run().await?,
+        CastSubcommand::Abi(AbiSubcommand::B2EPayload(cmd)) => cmd.run().await?,
+        CastSubcommand::Abi(AbiSubcommand::PrettyCalldata { calldata, offline }) => {
             let calldata = stdin::unwrap_line(calldata)?;
             print_scalar(pretty_calldata(&calldata, offline).await?.to_string())?;
         }
         // JSON: --optimize conflicts with --json at the clap level; optimize=None uses print_scalar
-        CastSubcommand::Sig { sig, optimize } => {
+        CastSubcommand::Abi(AbiSubcommand::Sig { sig, optimize }) => {
             let sig = stdin::unwrap_line(sig)?;
             match optimize {
                 Some(opt) => {
@@ -499,8 +516,8 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
         }
 
         // Blockchain & RPC queries
-        CastSubcommand::AccessList(cmd) => cmd.run().await?,
-        CastSubcommand::Age { block, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::AccessList(cmd)) => cmd.run().await?,
+        CastSubcommand::Query(QuerySubcommand::Age { block, rpc }) => {
             let timestamp = rpc_provider(&rpc)?
                 .get_block(block.unwrap_or_default())
                 .await?
@@ -514,7 +531,14 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 .format("%a %b %e %H:%M:%S %Y");
             print_scalar(format!("{age} UTC"))?;
         }
-        CastSubcommand::Balance { block, who, ether, rpc, erc20, overrides } => {
+        CastSubcommand::Query(QuerySubcommand::Balance {
+            block,
+            who,
+            ether,
+            rpc,
+            erc20,
+            overrides,
+        }) => {
             if erc20.is_none() && !overrides.is_empty() {
                 eyre::bail!("call overrides require `--erc20` when using `cast balance`");
             }
@@ -544,7 +568,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 }
             }
         }
-        CastSubcommand::BaseFee { block, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::BaseFee { block, rpc }) => {
             let fee = rpc_provider(&rpc)?
                 .get_block(block.unwrap_or_default())
                 .await?
@@ -554,7 +578,14 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 .ok_or_eyre("base fee not found")?;
             print_scalar(fee.to_string())?;
         }
-        CastSubcommand::Block { block, full, fields, raw, rpc, network } => {
+        CastSubcommand::Query(QuerySubcommand::Block {
+            block,
+            full,
+            fields,
+            raw,
+            rpc,
+            network,
+        }) => {
             let config = rpc.load_config()?;
             #[cfg(feature = "base")]
             let network = if network.is_none() && (raw || fields.iter().any(|f| f == "raw")) {
@@ -615,7 +646,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_json_value_or_scalar(output)?;
         }
-        CastSubcommand::BlockNumber { rpc, block } => {
+        CastSubcommand::Query(QuerySubcommand::BlockNumber { rpc, block }) => {
             let provider = rpc_provider(&rpc)?;
             let number = match block {
                 Some(id) => {
@@ -630,8 +661,8 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_scalar(number)?;
         }
-        CastSubcommand::Bal(cmd) => cmd.run().await?,
-        CastSubcommand::Chain { rpc } => {
+        CastSubcommand::Query(QuerySubcommand::Bal(cmd)) => cmd.run().await?,
+        CastSubcommand::Query(QuerySubcommand::Chain { rpc }) => {
             let provider = rpc_provider(&rpc)?;
             const GENESIS_CHAINS: &[(&str, &str)] = &[
                 ("0xa3c565fc15c7478862d50ccd6561e3c06b24cc509bf388941c25ea985ce32cb9", "kovan"),
@@ -737,13 +768,13 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_scalar(chain)?;
         }
-        CastSubcommand::ChainId { rpc } => {
+        CastSubcommand::Query(QuerySubcommand::ChainId { rpc }) => {
             print_scalar(rpc_provider(&rpc)?.get_chain_id().await?.to_string())?;
         }
-        CastSubcommand::Client { rpc } => {
+        CastSubcommand::Query(QuerySubcommand::Client { rpc }) => {
             print_scalar(rpc_provider(&rpc)?.get_client_version().await?)?;
         }
-        CastSubcommand::Code { block, who, disassemble, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::Code { block, who, disassemble, rpc }) => {
             let (provider, who) = rpc_provider_and_address(&rpc, who).await?;
             let code = provider.get_code_at(who).block_id(block.unwrap_or_default()).await?;
             print_scalar(if disassemble {
@@ -752,7 +783,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 code.to_string()
             })?;
         }
-        CastSubcommand::Codesize { block, who, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::Codesize { block, who, rpc }) => {
             let (provider, who) = rpc_provider_and_address(&rpc, who).await?;
             print_scalar(
                 provider
@@ -763,7 +794,14 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                     .to_string(),
             )?;
         }
-        CastSubcommand::ComputeAddress { address, nonce, salt, init_code, init_code_hash, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::ComputeAddress {
+            address,
+            nonce,
+            salt,
+            init_code,
+            init_code_hash,
+            rpc,
+        }) => {
             let address = stdin::unwrap_line(address)?;
             let salt = salt.unwrap_or(B256::ZERO);
             let computed = if let Some(init_code_hash) = init_code_hash {
@@ -780,11 +818,11 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_scalar(computed.to_checksum(None))?;
         }
-        CastSubcommand::Disassemble { bytecode } => {
+        CastSubcommand::Query(QuerySubcommand::Disassemble { bytecode }) => {
             let bytecode = stdin::unwrap_line(bytecode)?;
             print_scalar(crate::cmd::disassemble(&hex::decode(bytecode)?)?)?;
         }
-        CastSubcommand::Selectors { bytecode, resolve } => {
+        CastSubcommand::Query(QuerySubcommand::Selectors { bytecode, resolve }) => {
             let bytecode = stdin::unwrap_line(bytecode)?;
             let code = hex::decode(&bytecode)?;
             let info = evmole::contract_info(
@@ -864,11 +902,11 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 }
             }
         }
-        CastSubcommand::FindBlock(cmd) => cmd.run().await?,
-        CastSubcommand::GasPrice { rpc } => {
+        CastSubcommand::Query(QuerySubcommand::FindBlock(cmd)) => cmd.run().await?,
+        CastSubcommand::Query(QuerySubcommand::GasPrice { rpc }) => {
             print_scalar(rpc_provider(&rpc)?.get_gas_price().await?.to_string())?;
         }
-        CastSubcommand::Index { key_type, key, slot_number } => {
+        CastSubcommand::Query(QuerySubcommand::Index { key_type, key, slot_number }) => {
             let mut hasher = Keccak256::new();
 
             let k_ty = DynSolType::parse(&key_type).wrap_err("Could not parse type")?;
@@ -903,12 +941,12 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             let location = hasher.finalize();
             print_scalar(location.to_string())?;
         }
-        CastSubcommand::IndexErc7201 { id, formula_id } => {
+        CastSubcommand::Query(QuerySubcommand::IndexErc7201 { id, formula_id }) => {
             eyre::ensure!(formula_id == "erc7201", "unsupported formula ID: {formula_id}");
             let id = stdin::unwrap_line(id)?;
             print_scalar(foundry_common::erc7201(&id).to_string())?;
         }
-        CastSubcommand::Implementation { block, beacon, who, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::Implementation { block, beacon, who, rpc }) => {
             let (provider, who) = rpc_provider_and_address(&rpc, who).await?;
             // bytes32(uint256(keccak256('eip1967.proxy.beacon')) - 1)
             const BEACON_SLOT: B256 =
@@ -920,20 +958,20 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             let slot = if beacon { BEACON_SLOT } else { IMPLEMENTATION_SLOT };
             print_scalar(address_at_slot(&provider, who, slot, block).await?)?;
         }
-        CastSubcommand::Admin { block, who, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::Admin { block, who, rpc }) => {
             let (provider, who) = rpc_provider_and_address(&rpc, who).await?;
             // bytes32(uint256(keccak256('eip1967.proxy.admin')) - 1)
             const ADMIN_SLOT: B256 =
                 b256!("0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103");
             print_scalar(address_at_slot(&provider, who, ADMIN_SLOT, block).await?)?;
         }
-        CastSubcommand::Nonce { block, who, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::Nonce { block, who, rpc }) => {
             let (provider, who) = rpc_provider_and_address(&rpc, who).await?;
             print_scalar(
                 provider.get_transaction_count(who).block_id(block.unwrap_or_default()).await?,
             )?;
         }
-        CastSubcommand::Codehash { block, who, slots, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::Codehash { block, who, slots, rpc }) => {
             let (provider, who) = rpc_provider_and_address(&rpc, who).await?;
             print_scalar(
                 provider
@@ -944,7 +982,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                     .to_string(),
             )?;
         }
-        CastSubcommand::StorageRoot { block, who, slots, rpc } => {
+        CastSubcommand::Query(QuerySubcommand::StorageRoot { block, who, slots, rpc }) => {
             let (provider, who) = rpc_provider_and_address(&rpc, who).await?;
             print_scalar(
                 provider
@@ -955,7 +993,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                     .to_string(),
             )?;
         }
-        CastSubcommand::ChannelId {
+        CastSubcommand::Query(QuerySubcommand::ChannelId {
             payer,
             payee,
             token,
@@ -966,7 +1004,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             reserve,
             block,
             rpc,
-        } => {
+        }) => {
             let provider = rpc_provider(&rpc)?;
             let payer = payer.resolve(&provider).await?;
             let payee = payee.resolve(&provider).await?;
@@ -990,20 +1028,24 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 .await?;
             print_scalar(format!("{channel_id:#x}"))?;
         }
-        CastSubcommand::Proof { address, slots, rpc, block } => {
+        CastSubcommand::Query(QuerySubcommand::Proof { address, slots, rpc, block }) => {
             let (provider, address) = rpc_provider_and_address(&rpc, address).await?;
             let value =
                 provider.get_proof(address, slots).block_id(block.unwrap_or_default()).await?;
             print_json_object(value)?;
         }
-        CastSubcommand::Rpc(cmd) => cmd.run().await?,
-        CastSubcommand::Storage(cmd) => cmd.run().await?,
+        CastSubcommand::Query(QuerySubcommand::Rpc(cmd)) => cmd.run().await?,
+        CastSubcommand::Query(QuerySubcommand::Storage(cmd)) => cmd.run().await?,
 
         // Calls & transactions
-        CastSubcommand::Call(cmd) => cmd.run().await?,
-        CastSubcommand::Estimate(cmd) => cmd.run().await?,
-        CastSubcommand::MakeTx(cmd) => cmd.run().await?,
-        CastSubcommand::PublishTx { raw_tx, cast_async, rpc } => {
+        CastSubcommand::Transaction(TransactionSubcommand::Call(cmd)) => cmd.run().await?,
+        CastSubcommand::Transaction(TransactionSubcommand::Estimate(cmd)) => cmd.run().await?,
+        CastSubcommand::Transaction(TransactionSubcommand::MakeTx(cmd)) => cmd.run().await?,
+        CastSubcommand::Transaction(TransactionSubcommand::PublishTx {
+            raw_tx,
+            cast_async,
+            rpc,
+        }) => {
             let provider = rpc_provider(&rpc)?;
             let raw_tx = hex::decode(strip_0x(&raw_tx))?;
             let pending_tx = provider.send_raw_transaction(&raw_tx).await?;
@@ -1013,7 +1055,13 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 print_json_object(pending_tx.get_receipt().await?)?;
             }
         }
-        CastSubcommand::Receipt { tx_hash, field, cast_async, confirmations, rpc } => {
+        CastSubcommand::Transaction(TransactionSubcommand::Receipt {
+            tx_hash,
+            field,
+            cast_async,
+            confirmations,
+            rpc,
+        }) => {
             // JSON: The receipt helper already formats the output.
             sh_println!(
                 "{}",
@@ -1022,16 +1070,26 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                     .await?
             )?
         }
-        CastSubcommand::Run(cmd) => cmd.run().await?,
-        CastSubcommand::SendTx(cmd) => cmd.run().await?,
-        CastSubcommand::BatchMakeTx(cmd) => cmd.run().await?,
-        CastSubcommand::BatchSend(cmd) => cmd.run().await?,
-        CastSubcommand::Classify { raw_tx } => {
+        CastSubcommand::Transaction(TransactionSubcommand::Run(cmd)) => cmd.run().await?,
+        CastSubcommand::Transaction(TransactionSubcommand::SendTx(cmd)) => cmd.run().await?,
+        CastSubcommand::Transaction(TransactionSubcommand::BatchMakeTx(cmd)) => cmd.run().await?,
+        CastSubcommand::Transaction(TransactionSubcommand::BatchSend(cmd)) => cmd.run().await?,
+        CastSubcommand::Transaction(TransactionSubcommand::Classify { raw_tx }) => {
             let raw_tx = hex::decode(stdin::unwrap_line(raw_tx)?)?;
             let out = format_lane_classification(&raw_tx, "failed to decode raw transaction")?;
             print_json_value_or_scalar(out)?
         }
-        CastSubcommand::Tx { tx_hash, from, nonce, field, raw, lane, rpc, to_request, network } => {
+        CastSubcommand::Transaction(TransactionSubcommand::Tx {
+            tx_hash,
+            from,
+            nonce,
+            field,
+            raw,
+            lane,
+            rpc,
+            to_request,
+            network,
+        }) => {
             let config = rpc.load_config()?;
             #[cfg(feature = "base")]
             let network = match network {
@@ -1084,7 +1142,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
         }
 
         // 4Byte
-        CastSubcommand::FourByte { selector } => {
+        CastSubcommand::Abi(AbiSubcommand::FourByte { selector }) => {
             let selector = stdin::unwrap_line(selector)?;
             let sigs = decode_function_selector(selector).await?;
             if sigs.is_empty() {
@@ -1095,7 +1153,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
 
         // JSON envelope intentionally unsupported: output combines an interactive selector
         // disambiguation step with decoded token output; no single stable shape exists.
-        CastSubcommand::FourByteCalldata { calldata } => {
+        CastSubcommand::Abi(AbiSubcommand::FourByteCalldata { calldata }) => {
             let calldata = stdin::unwrap_line(calldata)?;
 
             if calldata.len() == 10 {
@@ -1126,7 +1184,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             print_tokens(&abi_decode_calldata(sig, &calldata, true, true)?)?;
         }
 
-        CastSubcommand::FourByteEvent { topic } => {
+        CastSubcommand::Abi(AbiSubcommand::FourByteEvent { topic }) => {
             let topic = stdin::unwrap_line(topic)?;
             let sigs = decode_event_topic(topic).await?;
             if sigs.is_empty() {
@@ -1136,7 +1194,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
         }
         // JSON envelope intentionally unsupported: output is a human-readable summary from an
         // external selector registry API with no stable machine-readable schema.
-        CastSubcommand::UploadSignature { signatures } => {
+        CastSubcommand::Abi(AbiSubcommand::UploadSignature { signatures }) => {
             let signatures = stdin::unwrap_vec(signatures)?;
             let ParsedSignatures { signatures, abis } = parse_signatures(signatures);
             if !abis.is_empty() {
@@ -1148,10 +1206,10 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
         }
 
         // ENS
-        CastSubcommand::Namehash { name } => {
+        CastSubcommand::Query(QuerySubcommand::Namehash { name }) => {
             print_scalar(namehash(&stdin::unwrap_line(name)?).to_string())?;
         }
-        CastSubcommand::LookupAddress { who, rpc, verify } => {
+        CastSubcommand::Query(QuerySubcommand::LookupAddress { who, rpc, verify }) => {
             let provider = rpc_provider(&rpc)?;
             let who = stdin::unwrap_line(who)?;
             let name = provider.lookup_address(&who).await?;
@@ -1164,7 +1222,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             }
             print_scalar(name)?;
         }
-        CastSubcommand::ResolveName { who, rpc, verify } => {
+        CastSubcommand::Query(QuerySubcommand::ResolveName { who, rpc, verify }) => {
             let provider = rpc_provider(&rpc)?;
             let who = stdin::unwrap_line(who)?;
             let address = provider
@@ -1182,7 +1240,7 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
         }
 
         // Misc
-        CastSubcommand::Keccak { data } => {
+        CastSubcommand::Misc(MiscSubcommand::Keccak { data }) => {
             let bytes = match data {
                 Some(data) => data.into_bytes(),
                 None => stdin::read_bytes(false)?,
@@ -1201,32 +1259,32 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_scalar(out)?;
         }
-        CastSubcommand::HashMessage { message } => {
+        CastSubcommand::Misc(MiscSubcommand::HashMessage { message }) => {
             print_scalar(eip191_hash_message(stdin::unwrap(message, false)?).to_string())?;
         }
-        CastSubcommand::SigEvent { event_string } => {
+        CastSubcommand::Misc(MiscSubcommand::SigEvent { event_string }) => {
             let event = get_event(&stdin::unwrap_line(event_string)?)?;
             print_scalar(format!("{:?}", event.selector()))?;
         }
-        CastSubcommand::LeftShift { value, bits, base_in, base_out } => {
+        CastSubcommand::Misc(MiscSubcommand::LeftShift { value, bits, base_in, base_out }) => {
             print_scalar(shift(&value, &bits, base_in.as_deref(), &base_out, |value, bits| {
                 value << bits
             })?)?;
         }
-        CastSubcommand::RightShift { value, bits, base_in, base_out } => {
+        CastSubcommand::Misc(MiscSubcommand::RightShift { value, bits, base_in, base_out }) => {
             print_scalar(shift(&value, &bits, base_in.as_deref(), &base_out, |value, bits| {
                 value.wrapping_shr(bits.saturating_to())
             })?)?;
         }
         // TODO(json): multi-line source code or directory expansion, needs structured envelope
-        CastSubcommand::Source {
+        CastSubcommand::Misc(MiscSubcommand::Source {
             address,
             directory,
             explorer_api_url,
             explorer_url,
             etherscan,
             flatten,
-        } => {
+        }) => {
             let config = etherscan.load_config()?;
             let chain = config.chain.unwrap_or_default();
             let api_key = config.get_etherscan_api_key(Some(chain));
@@ -1258,15 +1316,15 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
                 }
             }
         }
-        CastSubcommand::Create2(cmd) => cmd.execute()?,
-        CastSubcommand::Wallet { command } => command.run().await?,
-        CastSubcommand::Safe { command } => command.run().await?,
-        CastSubcommand::Completions { shell } => {
+        CastSubcommand::Misc(MiscSubcommand::Create2(cmd)) => cmd.execute()?,
+        CastSubcommand::Misc(MiscSubcommand::Wallet { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Safe { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Completions { shell }) => {
             generate(shell, &mut CastArgs::command(), "cast", &mut std::io::stdout())
         }
-        CastSubcommand::Logs(cmd) => cmd.run().await?,
-        CastSubcommand::Events(cmd) => cmd.run().await?,
-        CastSubcommand::DecodeTransaction { tx, network } => {
+        CastSubcommand::Misc(MiscSubcommand::Logs(cmd)) => cmd.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Events(cmd)) => cmd.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::DecodeTransaction { tx, network }) => {
             let tx = stdin::unwrap_line(tx)?;
             let decoded_tx = match network {
                 #[cfg(feature = "optimism")]
@@ -1284,24 +1342,24 @@ pub async fn run_command(args: CastArgs) -> Result<()> {
             };
             print_json_object(decoded_tx)?;
         }
-        CastSubcommand::RecoverAuthority { auth } => {
+        CastSubcommand::Misc(MiscSubcommand::RecoverAuthority { auth }) => {
             let auth: SignedAuthorization = serde_json::from_str(&auth)?;
             print_scalar(auth.recover_authority()?.to_string())?;
         }
-        CastSubcommand::TxPool { command } => command.run().await?,
-        CastSubcommand::Erc20Token { command } => command.run().await?,
-        CastSubcommand::Erc4626 { command } => command.run().await?,
-        CastSubcommand::Tip20Token { command } => command.run().await?,
-        CastSubcommand::ReceivePolicy { command } => command.run().await?,
-        CastSubcommand::Tip403 { command } => command.run().await?,
-        CastSubcommand::StorageCredits { command } => command.run().await?,
-        CastSubcommand::Keychain { command } => command.run().await?,
-        CastSubcommand::KeyAuthorization { command } => command.run().await?,
-        CastSubcommand::Tempo(args) => args.run().await?,
-        CastSubcommand::VirtualAddress { command } => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::TxPool { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Erc20Token { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Erc4626 { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Tip20Token { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::ReceivePolicy { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Tip403 { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::StorageCredits { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Keychain { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::KeyAuthorization { command }) => command.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Tempo(args)) => args.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::VirtualAddress { command }) => command.run().await?,
         #[cfg(any(feature = "base", feature = "optimism"))]
-        CastSubcommand::DAEstimate(cmd) => cmd.run().await?,
-        CastSubcommand::Trace(cmd) => cmd.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::DAEstimate(cmd)) => cmd.run().await?,
+        CastSubcommand::Misc(MiscSubcommand::Trace(cmd)) => cmd.run().await?,
     };
 
     Ok(())
```

### crates/cast/src/opts.rs
```diff
@@ -66,8 +66,33 @@ pub struct Cast {
     pub cmd: CastSubcommand,
 }
 
+/// The `cast` subcommands.
+///
+/// Subcommands are declared across several flattened enums because clap's derive generates one
+/// `augment_subcommands` function per enum, and in debug builds a single enum holding every
+/// subcommand produced a stack frame that overflowed the 2 MiB stack of test threads.
 #[derive(Subcommand)]
+#[allow(clippy::large_enum_variant, reason = "parsed once per process")]
 pub enum CastSubcommand {
+    #[command(flatten)]
+    Conversion(ConversionSubcommand),
+
+    #[command(flatten)]
+    Transaction(TransactionSubcommand),
+
+    #[command(flatten)]
+    Abi(AbiSubcommand),
+
+    #[command(flatten)]
+    Query(QuerySubcommand),
+
+    #[command(flatten)]
+    Misc(MiscSubcommand),
+}
+
+/// Constant and conversion subcommands.
+#[derive(Subcommand)]
+pub enum ConversionSubcommand {
     /// Prints the maximum value of the given integer type.
     #[command(visible_aliases = &["--max-int", "maxi"])]
     MaxInt {
@@ -239,42 +264,6 @@ pub enum CastSubcommand {
         value: Option<String>,
     },
 
-    /// Perform a left shifting operation
-    #[command(name = "shl")]
-    LeftShift {
-        /// The value to shift.
-        value: String,
-
-        /// The number of bits to shift.
-        bits: String,
-
-        /// The input base.
-        #[arg(long)]
-        base_in: Option<String>,
-
-        /// The output base.
-        #[arg(long, default_value = "16")]
-        base_out: String,
-    },
-
-    /// Perform a right shifting operation
-    #[command(name = "shr")]
-    RightShift {
-        /// The value to shift.
-        value: String,
-
-        /// The number of bits to shift.
-        bits: String,
-
-        /// The input base,
-        #[arg(long)]
-        base_in: Option<String>,
-
-        /// The output base,
-        #[arg(long, default_value = "16")]
-        base_out: String,
-    },
-
     /// Convert an ETH amount into another unit (ether, gwei or wei)
     ///
     /// Examples:
@@ -407,84 +396,32 @@ pub enum CastSubcommand {
         #[arg(value_name = "BASE")]
         base_out: Option<String>,
     },
-    /// Create an access list for a transaction
-    ///
-    /// Examples:
-    /// - cast access-list vitalik.eth --value 0.1ether
-    /// - cast access-list $TOKEN "transfer(address,uint256)" vitalik.eth 100
-    #[command(verbatim_doc_comment, visible_aliases = &["ac", "acl"])]
-    AccessList(AccessListArgs),
-    /// Get logs by signature or topic
-    ///
-    /// Event declarations decode matching logs in text output. Indexed parameters must be marked
-    /// `indexed` in the declaration. JSON output remains raw.
-    ///
-    /// Examples:
-    /// - cast logs "Transfer(address indexed from, address indexed to, uint256 value)"
-    /// - cast logs --address $TOKEN --from-block 21000000 --to-block latest $TOPIC_0
-    #[command(verbatim_doc_comment, visible_alias = "l")]
-    Logs(LogsArgs),
-    /// Fetch and decode events from a transaction receipt or log filter.
-    ///
-    /// Examples:
-    /// - cast events $TX_HASH
-    /// - cast events --tx-hash $TX_HASH
-    /// - cast events --address $TOKEN --from-block 21000000 --to-block latest
-    /// - cast events --address $TOKEN "Transfer(address indexed,address indexed,uint256)"
-    ///
-    /// A lone 32-byte positional value is treated as a transaction hash. Qualify a raw topic with
-    /// an address, block range, additional topic, or query size.
-    #[command(verbatim_doc_comment, visible_alias = "ev")]
-    Events(EventsArgs),
-    /// Get information about a block
-    ///
-    /// Examples:
-    /// - cast block latest
-    /// - cast block 21000000 --field timestamp
-    /// - cast block latest --json
-    #[command(verbatim_doc_comment, visible_alias = "bl")]
-    Block {
-        /// The block height to query at.
-        ///
-        /// Can also be the tags earliest, finalized, safe, latest, or pending.
-        block: Option<BlockId>,
-
-        /// If specified, only get the given field of the block.
-        #[arg(short, long = "field", aliases = ["fields"], num_args = 0.., action = ArgAction::Append, value_delimiter = ',')]
-        fields: Vec<String>,
-
-        /// Print the raw RLP encoded block header.
-        #[arg(long, conflicts_with = "fields")]
-        raw: bool,
-
-        #[arg(long, env = "CAST_FULL_BLOCK")]
-        full: bool,
 
-        #[command(flatten)]
-        rpc: RpcOpts,
-
-        /// Specify the Network for correct encoding.
-        #[arg(long, short, num_args = 1, value_name = "NETWORK")]
-        network: Option<NetworkVariant>,
+    /// Formats a string into bytes32 encoding.
+    #[command(name = "format-bytes32-string", visible_aliases = &["--format-bytes32-string"])]
+    FormatBytes32String {
+        /// The string to format.
+        string: Option<String>,
     },
 
-    /// Get the latest block number.
-    #[command(visible_alias = "bn")]
-    BlockNumber {
-        /// The hash or tag to query. If not specified, the latest number is returned.
-        block: Option<BlockId>,
-        #[command(flatten)]
-        rpc: RpcOpts,
+    /// Parses a string from bytes32 encoding.
+    #[command(name = "parse-bytes32-string", visible_aliases = &["--parse-bytes32-string"])]
+    ParseBytes32String {
+        /// The string to parse.
+        bytes: Option<String>,
     },
 
-    /// Get the EIP-7928 block access list of a block
-    ///
-    /// Examples:
-    /// - cast bal latest
-    /// - cast bal 21000000 --raw
-    #[command(verbatim_doc_comment, visible_alias = "block-access-list")]
-    Bal(BalArgs),
+    #[command(name = "parse-bytes32-address", visible_aliases = &["--parse-bytes32-address"])]
+    #[command(about = "Parses a checksummed address from bytes32 encoding.")]
+    ParseBytes32Address {
+        #[arg(value_name = "BYTES")]
+        bytes: Option<String>,
+    },
+}
 
+/// Call and transaction subcommands.
+#[derive(Subcommand)]
+pub enum TransactionSubcommand {
     /// Perform a call on an account without publishing a transaction
     ///
     /// Examples:
@@ -493,84 +430,6 @@ pub enum CastSubcommand {
     #[command(verbatim_doc_comment, visible_alias = "c")]
     Call(CallArgs),
 
-    /// ABI-encode a function with arguments.
-    #[command(name = "calldata", visible_alias = "cd")]
-    CalldataEncode {
-        /// The function signature in the format `<name>(<in-types>)(<out-types>)`
-        sig: String,
-
-        /// The arguments to encode.
-        #[arg(allow_hyphen_values = true)]
-        args: Vec<String>,
-
-        // Path to file containing arguments to encode.
-        #[arg(long, value_name = "PATH")]
-        file: Option<PathBuf>,
-    },
-
-    /// Get the symbolic name of the current chain.
-    Chain {
-        #[command(flatten)]
-        rpc: RpcOpts,
-    },
-
-    /// Get the Ethereum chain ID.
-    #[command(visible_aliases = &["ci", "cid"])]
-    ChainId {
-        #[command(flatten)]
-        rpc: RpcOpts,
-    },
-
-    /// Get the current client version.
-    #[command(visible_alias = "cl")]
-    Client {
-        #[command(flatten)]
-        rpc: RpcOpts,
-    },
-
-    /// Compute the contract address from a given nonce and deployer address.
-    #[command(visible_alias = "ca")]
-    ComputeAddress {
-        /// The deployer address.
-        address: Option<Address>,
-
-        /// The nonce of the deployer address.
-        #[arg(
-            long,
-            conflicts_with = "salt",
-            conflicts_with = "init_code",
-            conflicts_with = "init_code_hash"
-        )]
-        nonce: Option<u64>,
-
-        /// The salt for CREATE2 address computation.
-        #[arg(long, conflicts_with = "nonce")]
-        salt: Option<B256>,
-
-        /// The init code for CREATE2 address computation.
-        #[arg(
-            long,
-            requires = "salt",
-            conflicts_with = "init_code_hash",
-            conflicts_with = "nonce"
-        )]
-        init_code: Option<String>,
-
-        /// The init code hash for CREATE2 address computation.
-        #[arg(long, requires = "salt", conflicts_with = "init_code", conflicts_with = "nonce")]
-        init_code_hash: Option<B256>,
-
-        #[command(flatten)]
-        rpc: RpcOpts,
-    },
-
-    /// Disassembles a hex-encoded bytecode into a human-readable representation.
-    #[command(visible_alias = "da")]
-    Disassemble {
-        /// The hex-encoded bytecode.
-        bytecode: Option<String>,
-    },
-
     /// Build and sign a transaction
     ///
     /// Examples:
@@ -585,10 +444,6 @@ pub enum CastSubcommand {
         raw_tx: Option<String>,
     },
 
-    /// Calculate the ENS namehash of a name.
-    #[command(visible_aliases = &["na", "nh"])]
-    Namehash { name: Option<String> },
-
     /// Get information about a transaction
     ///
     /// Examples:
@@ -696,6 +551,38 @@ pub enum CastSubcommand {
     #[command(verbatim_doc_comment, visible_alias = "e")]
     Estimate(EstimateArgs),
 
+    /// Runs a published transaction in a local environment and prints the trace
+    ///
+    /// If the node serves an EIP-7928 block access list (BAL) for the transaction's block, the
+    /// transaction's prestate is read from it instead of replaying the earlier transactions of
+    /// the block. Pass `--no-bal` to always replay the block.
+    ///
+    /// Examples:
+    /// - cast run $TX_HASH
+    /// - cast run $TX_HASH --quick (only use the state from the previous block)
+    /// - cast run $TX_HASH --debug (open the transaction in the debugger)
+    #[command(verbatim_doc_comment, visible_alias = "r")]
+    Run(RunArgs),
+}
+
+/// ABI encoding and decoding, selector and contract artifact subcommands.
+#[derive(Subcommand)]
+pub enum AbiSubcommand {
+    /// ABI-encode a function with arguments.
+    #[command(name = "calldata", visible_alias = "cd")]
+    CalldataEncode {
+        /// The function signature in the format `<name>(<in-types>)(<out-types>)`
+        sig: String,
+
+        /// The arguments to encode.
+        #[arg(allow_hyphen_values = true)]
+        args: Vec<String>,
+
+        // Path to file containing arguments to encode.
+        #[arg(long, value_name = "PATH")]
+        file: Option<PathBuf>,
+    },
+
     /// Decode ABI-encoded input data
     ///
     /// Similar to `abi-decode --input`, but function selector MUST be prefixed in `calldata`.
@@ -807,12 +694,237 @@ pub enum CastSubcommand {
         args: Vec<String>,
     },
 
-    /// Compute the storage slot for an entry in a mapping.
-    #[command(visible_alias = "in")]
-    Index {
-        /// The mapping key type.
-        key_type: String,
-
+    /// Get the function signatures for the given selector from <https://openchain.xyz>.
+    #[command(name = "4byte", visible_aliases = &["4", "4b"])]
+    FourByte {
+        /// The function selector.
+        selector: Option<Selector>,
+    },
+
+    /// Decode ABI-encoded calldata using <https://openchain.xyz>.
+    #[command(name = "4byte-calldata", aliases = &["4byte-decode", "4d", "4bd"], visible_aliases = &["4c", "4bc"])]
+    FourByteCalldata {
+        /// The ABI-encoded calldata.
+        calldata: Option<String>,
+    },
+
+    /// Get the event signature for a given topic 0 from <https://openchain.xyz>.
+    #[command(name = "4byte-event", visible_aliases = &["4e", "4be", "topic0-event", "t0e"])]
+    FourByteEvent {
+        /// Topic 0
+        #[arg(value_name = "TOPIC_0")]
+        topic: Option<B256>,
+    },
+
+    /// Upload the given signatures to <https://openchain.xyz>.
+    ///
+    /// Example inputs:
+    /// - "transfer(address,uint256)"
+    /// - "function transfer(address,uint256)"
+    /// - "function transfer(address,uint256)" "event Transfer(address,address,uint256)"
+    /// - "./out/Contract.sol/Contract.json"
+    #[command(visible_aliases = &["ups"])]
+    UploadSignature {
+        /// The signatures to upload.
+        ///
+        /// Prefix with 'function', 'event', or 'error'. Defaults to function if no prefix given.
+        /// Can also take paths to contract artifact JSON.
+        signatures: Vec<String>,
+    },
+
+    /// Pretty print calldata.
+    ///
+    /// Tries to decode the calldata using <https://openchain.xyz> unless --offline is passed.
+    #[command(visible_alias = "pc")]
+    PrettyCalldata {
+        /// The calldata.
+        calldata: Option<String>,
+
+        /// Skip the <https://openchain.xyz> lookup.
+        #[arg(long, short)]
+        offline: bool,
+    },
+
+    /// Download a contract creation code from Etherscan and RPC.
+    #[command(visible_alias = "cc")]
+    CreationCode(CreationCodeArgs),
+
+    /// Generate an artifact file, that can be used to deploy a contract locally.
+    #[command(visible_alias = "ar")]
+    Artifact(ArtifactArgs),
+
+    /// Display constructor arguments used for the contract initialization.
+    #[command(visible_alias = "cra")]
+    ConstructorArgs(ConstructorArgsArgs),
+
+    /// Generate a Solidity interface from a given ABI
+    ///
+    /// Currently does not support ABI encoder v2.
+    ///
+    /// Examples:
+    /// - cast interface $TOKEN --etherscan-api-key $KEY (fetch the ABI from Etherscan)
+    /// - cast interface ./out/Counter.sol/Counter.json (load a local ABI file)
+    #[command(verbatim_doc_comment, visible_alias = "i")]
+    Interface(InterfaceArgs),
+
+    /// Generate a rust binding from a given ABI.
+    #[command(visible_alias = "bi")]
+    Bind(BindArgs),
+
+    /// Convert Beacon payload to execution payload.
+    #[command(visible_alias = "b2e")]
+    B2EPayload(B2EPayloadArgs),
+
+    /// Get the selector for a function
+    ///
+    /// Examples:
+    /// - cast sig "transfer(address,uint256)"
+    /// - cast sig "deposit(uint256)" 2 (optimize for 2 leading zero bytes)
+    #[command(verbatim_doc_comment, visible_alias = "si")]
+    Sig {
+        /// The function signature, e.g. transfer(address,uint256).
+        sig: Option<String>,
+
+        /// Optimize signature to contain provided amount of leading zeroes in selector.
+        #[arg(conflicts_with = "json")]
+        optimize: Option<usize>,
+    },
+}
+
+/// Blockchain, RPC and ENS query subcommands.
+#[derive(Subcommand)]
+#[allow(clippy::large_enum_variant, reason = "parsed once per process")]
+pub enum QuerySubcommand {
+    /// Create an access list for a transaction
+    ///
+    /// Examples:
+    /// - cast access-list vitalik.eth --value 0.1ether
+    /// - cast access-list $TOKEN "transfer(address,uint256)" vitalik.eth 100
+    #[command(verbatim_doc_comment, visible_aliases = &["ac", "acl"])]
+    AccessList(AccessListArgs),
+
+    /// Get information about a block
+    ///
+    /// Examples:
+    /// - cast block latest
+    /// - cast block 21000000 --field timestamp
+    /// - cast block latest --json
+    #[command(verbatim_doc_comment, visible_alias = "bl")]
+    Block {
+        /// The block height to query at.
+        ///
+        /// Can also be the tags earliest, finalized, safe, latest, or pending.
+        block: Option<BlockId>,
+
+        /// If specified, only get the given field of the block.
+        #[arg(short, long = "field", aliases = ["fields"], num_args = 0.., action = ArgAction::Append, value_delimiter = ',')]
+        fields: Vec<String>,
+
+        /// Print the raw RLP encoded block header.
+        #[arg(long, conflicts_with = "fields")]
+        raw: bool,
+
+        #[arg(long, env = "CAST_FULL_BLOCK")]
+        full: bool,
+
+        #[command(flatten)]
+        rpc: RpcOpts,
+
+        /// Specify the Network for correct encoding.
+        #[arg(long, short, num_args = 1, value_name = "NETWORK")]
+        network: Option<NetworkVariant>,
+    },
+
+    /// Get the latest block number.
+    #[command(visible_alias = "bn")]
+    BlockNumber {
+        /// The hash or tag to query. If not specified, the latest number is returned.
+        block: Option<BlockId>,
+        #[command(flatten)]
+        rpc: RpcOpts,
+    },
+
+    /// Get the EIP-7928 block access list of a block
+    ///
+    /// Examples:
+    /// - cast bal latest
+    /// - cast bal 21000000 --raw
+    #[command(verbatim_doc_comment, visible_alias = "block-access-list")]
+    Bal(BalArgs),
+
+    /// Get the symbolic name of the current chain.
+    Chain {
+        #[command(flatten)]
+        rpc: RpcOpts,
+    },
+
+    /// Get the Ethereum chain ID.
+    #[command(visible_aliases = &["ci", "cid"])]
+    ChainId {
+        #[command(flatten)]
+        rpc: RpcOpts,
+    },
+
+    /// Get the current client version.
+    #[command(visible_alias = "cl")]
+    Client {
+        #[command(flatten)]
+        rpc: RpcOpts,
+    },
+
+    /// Compute the contract address from a given nonce and deployer address.
+    #[command(visible_alias = "ca")]
+    ComputeAddress {
+        /// The deployer address.
+        address: Option<Address>,
+
+        /// The nonce of the deployer address.
+        #[arg(
+            long,
+            conflicts_with = "salt",
+            conflicts_with = "init_code",
+            conflicts_with = "init_code_hash"
+        )]
+        nonce: Option<u64>,
+
+        /// The salt for CREATE2 address computation.
+        #[arg(long, conflicts_with = "nonce")]
+        salt: Option<B256>,
+
+        /// The init code for CREATE2 address computation.
+        #[arg(
+            long,
+            requires = "salt",
+            conflicts_with = "init_code_hash",
+            conflicts_with = "nonce"
+        )]
+        init_code: Option<String>,
+
+        /// The init code hash for CREATE2 address computation.
+        #[arg(long, requires = "salt", conflicts_with = "init_code", conflicts_with = "nonce")]
+        init_code_hash: Option<B256>,
+
+        #[command(flatten)]
+        rpc: RpcOpts,
+    },
+
+    /// Disassembles a hex-encoded bytecode into a human-readable representation.
+    #[command(visible_alias = "da")]
+    Disassemble {
+        /// The hex-encoded bytecode.
+        bytecode: Option<String>,
+    },
+
+    /// Calculate the ENS namehash of a name.
+    #[command(visible_aliases = &["na", "nh"])]
+    Namehash { name: Option<String> },
+
+    /// Compute the storage slot for an entry in a mapping.
+    #[command(visible_alias = "in")]
+    Index {
+        /// The mapping key type.
+        key_type: String,
+
         /// The mapping key.
         key: String,
 
@@ -863,63 +975,12 @@ pub enum CastSubcommand {
         #[arg(long, short = 'B')]
         block: Option<BlockId>,
 
-        /// The address from which the admin account will be fetched.
-        #[arg(value_parser = NameOrAddress::from_str)]
-        who: NameOrAddress,
-
-        #[command(flatten)]
-        rpc: RpcOpts,
-    },
-
-    /// Get the function signatures for the given selector from <https://openchain.xyz>.
-    #[command(name = "4byte", visible_aliases = &["4", "4b"])]
-    FourByte {
-        /// The function selector.
-        selector: Option<Selector>,
-    },
-
-    /// Decode ABI-encoded calldata using <https://openchain.xyz>.
-    #[command(name = "4byte-calldata", aliases = &["4byte-decode", "4d", "4bd"], visible_aliases = &["4c", "4bc"])]
-    FourByteCalldata {
-        /// The ABI-encoded calldata.
-        calldata: Option<String>,
-    },
-
-    /// Get the event signature for a given topic 0 from <https://openchain.xyz>.
-    #[command(name = "4byte-event", visible_aliases = &["4e", "4be", "topic0-event", "t0e"])]
-    FourByteEvent {
-        /// Topic 0
-        #[arg(value_name = "TOPIC_0")]
-        topic: Option<B256>,
-    },
-
-    /// Upload the given signatures to <https://openchain.xyz>.
-    ///
-    /// Example inputs:
-    /// - "transfer(address,uint256)"
-    /// - "function transfer(address,uint256)"
-    /// - "function transfer(address,uint256)" "event Transfer(address,address,uint256)"
-    /// - "./out/Contract.sol/Contract.json"
-    #[command(visible_aliases = &["ups"])]
-    UploadSignature {
-        /// The signatures to upload.
-        ///
-        /// Prefix with 'function', 'event', or 'error'. Defaults to function if no prefix given.
-        /// Can also take paths to contract artifact JSON.
-        signatures: Vec<String>,
-    },
-
-    /// Pretty print calldata.
-    ///
-    /// Tries to decode the calldata using <https://openchain.xyz> unless --offline is passed.
-    #[command(visible_alias = "pc")]
-    PrettyCalldata {
-        /// The calldata.
-        calldata: Option<String>,
+        /// The address from which the admin account will be fetched.
+        #[arg(value_parser = NameOrAddress::from_str)]
+        who: NameOrAddress,
 
-        /// Skip the <https://openchain.xyz> lookup.
-        #[arg(long, short)]
-        offline: bool,
+        #[command(flatten)]
+        rpc: RpcOpts,
     },
 
     /// Get the timestamp of a block.
@@ -1028,32 +1089,6 @@ pub enum CastSubcommand {
         rpc: RpcOpts,
     },
 
-    /// Generate event signatures from event string.
-    #[command(visible_alias = "se")]
-    SigEvent {
-        /// The event string.
-        event_string: Option<String>,
-    },
-
-    /// Hash arbitrary data using Keccak-256
-    ///
-    /// Examples:
-    /// - cast keccak "hello world"
-    /// - cast keccak 0xdeadbeef
-    /// - echo -n "some data" | cast keccak (hash data from stdin)
-    #[command(verbatim_doc_comment, visible_aliases = &["k", "keccak256"])]
-    Keccak {
-        /// The data to hash.
-        data: Option<String>,
-    },
-
-    /// Hash a message according to EIP-191.
-    #[command(visible_aliases = &["--hash-message", "hm"])]
-    HashMessage {
-        /// The message to hash.
-        message: Option<String>,
-    },
-
     /// Perform an ENS lookup.
     #[command(visible_alias = "rn")]
     ResolveName {
@@ -1214,6 +1249,120 @@ pub enum CastSubcommand {
         rpc: RpcOpts,
     },
 
+    /// Get the block number closest to the provided timestamp.
+    #[command(visible_alias = "f")]
+    FindBlock(FindBlockArgs),
+
+    /// Perform a raw JSON-RPC request
+    ///
+    /// Examples:
+    /// - cast rpc eth_blockNumber
+    /// - cast rpc eth_getBlockByNumber 0x123 false
+    /// - cast rpc eth_getBlockByNumber '["0x123", false]' --raw
+    #[command(verbatim_doc_comment, visible_alias = "rp")]
+    Rpc(RpcArgs),
+
+    /// Extracts function selectors and arguments from bytecode
+    #[command(visible_alias = "sel")]
+    Selectors {
+        /// The hex-encoded bytecode.
+        bytecode: Option<String>,
+
+        /// Resolve the function signatures for the extracted selectors using <https://openchain.xyz>
+        #[arg(long, short)]
+        resolve: bool,
+    },
+}
+
+/// Miscellaneous subcommands.
+#[derive(Subcommand)]
+pub enum MiscSubcommand {
+    /// Perform a left shifting operation
+    #[command(name = "shl")]
+    LeftShift {
+        /// The value to shift.
+        value: String,
+
+        /// The number of bits to shift.
+        bits: String,
+
+        /// The input base.
+        #[arg(long)]
+        base_in: Option<String>,
+
+        /// The output base.
+        #[arg(long, default_value = "16")]
+        base_out: String,
+    },
+
+    /// Perform a right shifting operation
+    #[command(name = "shr")]
+    RightShift {
+        /// The value to shift.
+        value: String,
+
+        /// The number of bits to shift.
+        bits: String,
+
+        /// The input base,
+        #[arg(long)]
+        base_in: Option<String>,
+
+        /// The output base,
+        #[arg(long, default_value = "16")]
+        base_out: String,
+    },
+
+    /// Get logs by signature or topic
+    ///
+    /// Event declarations decode matching logs in text output. Indexed parameters must be marked
+    /// `indexed` in the declaration. JSON output remains raw.
+    ///
+    /// Examples:
+    /// - cast logs "Transfer(address indexed from, address indexed to, uint256 value)"
+    /// - cast logs --address $TOKEN --from-block 21000000 --to-block latest $TOPIC_0
+    #[command(verbatim_doc_comment, visible_alias = "l")]
+    Logs(LogsArgs),
+
+    /// Fetch and decode events from a transaction receipt or log filter.
+    ///
+    /// Examples:
+    /// - cast events $TX_HASH
+    /// - cast events --tx-hash $TX_HASH
+    /// - cast events --address $TOKEN --from-block 21000000 --to-block latest
+    /// - cast events --address $TOKEN "Transfer(address indexed,address indexed,uint256)"
+    ///
+    /// A lone 32-byte positional value is treated as a transaction hash. Qualify a raw topic with
+    /// an address, block range, additional topic, or query size.
+    #[command(verbatim_doc_comment, visible_alias = "ev")]
+    Events(EventsArgs),
+
+    /// Generate event signatures from event string.
+    #[command(visible_alias = "se")]
+    SigEvent {
+        /// The event string.
+        event_string: Option<String>,
+    },
+
+    /// Hash arbitrary data using Keccak-256
+    ///
+    /// Examples:
+    /// - cast keccak "hello world"
+    /// - cast keccak 0xdeadbeef
+    /// - echo -n "some data" | cast keccak (hash data from stdin)
+    #[command(verbatim_doc_comment, visible_aliases = &["k", "keccak256"])]
+    Keccak {
+        /// The data to hash.
+        data: Option<String>,
+    },
+
+    /// Hash a message according to EIP-191.
+    #[command(visible_aliases = &["--hash-message", "hm"])]
+    HashMessage {
+        /// The message to hash.
+        message: Option<String>,
+    },
+
     /// Get the source code of a contract from a block explorer.
     #[command(visible_aliases = &["et", "src"])]
     Source {
@@ -1254,108 +1403,17 @@ pub enum CastSubcommand {
         command: SafeSubcommand,
     },
 
-    /// Download a contract creation code from Etherscan and RPC.
-    #[command(visible_alias = "cc")]
-    CreationCode(CreationCodeArgs),
-
-    /// Generate an artifact file, that can be used to deploy a contract locally.
-    #[command(visible_alias = "ar")]
-    Artifact(ArtifactArgs),
-
-    /// Display constructor arguments used for the contract initialization.
-    #[command(visible_alias = "cra")]
-    ConstructorArgs(ConstructorArgsArgs),
-
-    /// Generate a Solidity interface from a given ABI
-    ///
-    /// Currently does not support ABI encoder v2.
-    ///
-    /// Examples:
-    /// - cast interface $TOKEN --etherscan-api-key $KEY (fetch the ABI from Etherscan)
-    /// - cast interface ./out/Counter.sol/Counter.json (load a local ABI file)
-    #[command(verbatim_doc_comment, visible_alias = "i")]
-    Interface(InterfaceArgs),
-
-    /// Generate a rust binding from a given ABI.
-    #[command(visible_alias = "bi")]
-    Bind(BindArgs),
-
-    /// Convert Beacon payload to execution payload.
-    #[command(visible_alias = "b2e")]
-    B2EPayload(B2EPayloadArgs),
-
-    /// Get the selector for a function
-    ///
-    /// Examples:
-    /// - cast sig "transfer(address,uint256)"
-    /// - cast sig "deposit(uint256)" 2 (optimize for 2 leading zero bytes)
-    #[command(verbatim_doc_comment, visible_alias = "si")]
-    Sig {
-        /// The function signature, e.g. transfer(address,uint256).
-        sig: Option<String>,
-
-        /// Optimize signature to contain provided amount of leading zeroes in selector.
-        #[arg(conflicts_with = "json")]
-        optimize: Option<usize>,
-    },
-
     /// Generate a deterministic contract address using CREATE2.
     #[command(visible_alias = "c2")]
     Create2(Create2Args),
 
-    /// Get the block number closest to the provided timestamp.
-    #[command(visible_alias = "f")]
-    FindBlock(FindBlockArgs),
-
     /// Generate shell completions script.
     #[command(visible_alias = "com")]
     Completions {
         #[arg(value_enum)]
         shell: foundry_cli::clap::Shell,
     },
 
-    /// Runs a published transaction in a local environment and prints the trace
-    ///
-    /// If the node serves an EIP-7928 block access list (BAL) for the transaction's block, the
-    /// transaction's prestate is read from it instead of replaying the earlier transactions of
-    /// the block. Pass `--no-bal` to always replay the block.
-    ///
-    /// Examples:
-    /// - cast run $TX_HASH
-    /// - cast run $TX_HASH --quick (only use the state from the previous block)
-    /// - cast run $TX_HASH --debug (open the transaction in the debugger)
-    #[command(verbatim_doc_comment, visible_alias = "r")]
-    Run(RunArgs),
-
-    /// Perform a raw JSON-RPC request
-    ///
-    /// Examples:
-    /// - cast rpc eth_blockNumber
-    /// - cast rpc eth_getBlockByNumber 0x123 false
-    /// - cast rpc eth_getBlockByNumber '["0x123", false]' --raw
-    #[command(verbatim_doc_comment, visible_alias = "rp")]
-    Rpc(RpcArgs),
-
-    /// Formats a string into bytes32 encoding.
-    #[command(name = "format-bytes32-string", visible_aliases = &["--format-bytes32-string"])]
-    FormatBytes32String {
-        /// The string to format.
-        string: Option<String>,
-    },
-
-    /// Parses a string from bytes32 encoding.
-    #[command(name = "parse-bytes32-string", visible_aliases = &["--parse-bytes32-string"])]
-    ParseBytes32String {
-        /// The string to parse.
-        bytes: Option<String>,
-    },
-    #[command(name = "parse-bytes32-address", visible_aliases = &["--parse-bytes32-address"])]
-    #[command(about = "Parses a checksummed address from bytes32 encoding.")]
-    ParseBytes32Address {
-        #[arg(value_name = "BYTES")]
-        bytes: Option<String>,
-    },
-
     /// Decodes a raw signed EIP 2718 typed transaction
     #[command(visible_aliases = &["dt", "decode-tx"])]
     DecodeTransaction {
@@ -1374,23 +1432,13 @@ pub enum CastSubcommand {
     #[command(visible_aliases = &["decode-auth"])]
     RecoverAuthority { auth: String },
 
-    /// Extracts function selectors and arguments from bytecode
-    #[command(visible_alias = "sel")]
-    Selectors {
-        /// The hex-encoded bytecode.
-        bytecode: Option<String>,
-
-        /// Resolve the function signatures for the extracted selectors using <https://openchain.xyz>
-        #[arg(long, short)]
-        resolve: bool,
-    },
-
     /// Inspect the TxPool of a node.
     #[command(visible_alias = "tp")]
     TxPool {
         #[command(subcommand)]
         command: TxPoolSubcommands,
     },
+
     /// Estimates the data availability size of a given opstack block.
     #[cfg(any(feature = "base", feature = "optimism"))]
     #[command(name = "da-estimate")]
@@ -1506,7 +1554,7 @@ mod tests {
             "0x01",
         ]);
         match args.cmd {
-            CastSubcommand::Proof { slots, .. } => {
+            CastSubcommand::Query(QuerySubcommand::Proof { slots, .. }) => {
                 assert_eq!(
                     slots,
                     vec![
@@ -1532,7 +1580,7 @@ mod tests {
             "2",
         ]);
         match args.cmd {
-            CastSubcommand::CalldataEncode { args, .. } => {
+            CastSubcommand::Abi(AbiSubcommand::CalldataEncode { args, .. }) => {
                 assert_eq!(
                     args,
                     vec!["5c9d55b78febcc2061715ba4f57ecf8ea2711f2c".to_string(), "2".to_string()]
@@ -1546,7 +1594,7 @@ mod tests {
     fn parse_call_data_with_file() {
         let args: Cast = Cast::parse_from(["foundry-cli", "calldata", "f()", "--file", "test.txt"]);
         match args.cmd {
-            CastSubcommand::CalldataEncode { sig, file, args } => {
+            CastSubcommand::Abi(AbiSubcommand::CalldataEncode { sig, file, args }) => {
                 assert_eq!(sig, "f()".to_string());
                 assert_eq!(file, Some(PathBuf::from("test.txt")));
                 assert!(args.is_empty());
@@ -1564,7 +1612,7 @@ mod tests {
             "__$_$__$$$$$__$$_$$$_$$__$$___$$(address,address,uint256)",
         ]);
         match args.cmd {
-            CastSubcommand::Sig { sig, .. } => {
+            CastSubcommand::Abi(AbiSubcommand::Sig { sig, .. }) => {
                 let sig = sig.unwrap();
                 assert_eq!(
                     sig,
```
