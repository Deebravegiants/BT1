# [?] Protect against OOB offset in variable list SSZ decoding (#974)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2020-04-20
Source: https://github.com/sigp/lighthouse/commit/b374ead24b052e57b492e8680bdd19d6cf251c71
Type: security-commit

## Details
Protect against OOB offset in variable list SSZ decoding (#974)

* Add "pretty-ssz" tool to lcli

* Protect against OOB SSZ offset

* Add more work on decoding

* Fix benches

* Add more decode fixes

* Rename fixed_ptr

* Add, fix tests

* Add extra test

* Increase SSZ decode error granularity

* Ripples new error types across ssz crate

* Add comment to `sanitize_offset`

* Introduce max_len to SSZ list decoding

* Restrict FixedVector, check for zero-len items

* Double check for empty list

* Address Michael's comment

## Patch
### eth2/utils/ssz/src/decode.rs
```diff
@@ -21,10 +21,72 @@ pub enum DecodeError {
     /// length items (i.e., `length[0] < BYTES_PER_LENGTH_OFFSET`).
     /// - When decoding variable-length items, the `n`'th offset was less than the `n-1`'th offset.
     OutOfBoundsByte { i: usize },
+    /// An offset points “backwards” into the fixed-bytes portion of the message, essentially
+    /// double-decoding bytes that will also be decoded as fixed-length.
+    ///
+    /// https://notes.ethereum.org/ruKvDXl6QOW3gnqVYb8ezA?view#1-Offset-into-fixed-portion
+    OffsetIntoFixedPortion(usize),
+    /// The first offset does not point to the byte that follows the fixed byte portion,
+    /// essentially skipping a variable-length byte.
+    ///
+    /// https://notes.ethereum.org/ruKvDXl6QOW3gnqVYb8ezA?view#2-Skip-first-variable-byte
+    OffsetSkipsVariableBytes(usize),
+    /// An offset points to bytes prior to the previous offset. Depending on how you look at it,
+    /// this either double-decodes bytes or makes the first offset a negative-length.
+    ///
+    /// https://notes.ethereum.org/ruKvDXl6QOW3gnqVYb8ezA?view#3-Offsets-are-decreasing
+    OffsetsAreDecreasing(usize),
+    /// An offset references byte indices that do not exist in the source bytes.
+    ///
+    /// https://notes.ethereum.org/ruKvDXl6QOW3gnqVYb8ezA?view#4-Offsets-are-out-of-bounds
+    OffsetOutOfBounds(usize),
+    /// A variable-length list does not have a fixed portion that is cleanly divisible by
+    /// `BYTES_PER_LENGTH_OFFSET`.
+    InvalidListFixedBytesLen(usize),
+    /// Some item has a `ssz_fixed_len` of zero. This is illegal.
+    ZeroLengthItem,
     /// The given bytes were invalid for some application-level reason.
     BytesInvalid(String),
 }
 
+/// Performs checks on the `offset` based upon the other parameters provided.
+///
+/// ## Detail
+///
+/// - `offset`: the offset bytes (e.g., result of `read_offset(..)`).
+/// - `previous_offset`: unless this is the first offset in the SSZ object, the value of the
+/// previously-read offset. Used to ensure offsets are not decreasing.
+/// - `num_bytes`: the total number of bytes in the SSZ object. Used to ensure the offset is not
+/// out of bounds.
+/// - `num_fixed_bytes`: the number of fixed-bytes in the struct, if it is known. Used to ensure
+/// that the first offset doesn't skip any variable bytes.
+///
+/// ## References
+///
+/// The checks here are derived from this document:
+///
+/// https://notes.ethereum.org/ruKvDXl6QOW3gnqVYb8ezA?view
+pub fn sanitize_offset(
+    offset: usize,
+    previous_offset: Option<usize>,
+    num_bytes: usize,
+    num_fixed_bytes: Option<usize>,
+) -> Result<usize, DecodeError> {
+    if num_fixed_bytes.map_or(false, |fixed_bytes| offset < fixed_bytes) {
+        Err(DecodeError::OffsetIntoFixedPortion(offset))
+    } else if previous_offset.is_none()
+        && num_fixed_bytes.map_or(false, |fixed_bytes| offset != fixed_bytes)
+    {
+        Err(DecodeError::OffsetSkipsVariableBytes(offset))
+    } else if offset > num_bytes {
+        Err(DecodeError::OffsetOutOfBounds(offset))
+    } else if previous_offset.map_or(false, |prev| prev > offset) {
+        Err(DecodeError::OffsetsAreDecreasing(offset))
+    } else {
+        Ok(offset)
+    }
+}
+
 /// Provides SSZ decoding (de-serialization) via the `from_ssz_bytes(&bytes)` method.
 ///
 /// See `examples/` for manual implementations or the crate root for implementations using
@@ -97,21 +159,14 @@ impl<'a> SszDecoderBuilder<'a> {
 
             self.items.push(slice);
         } else {
-            let offset = read_offset(&self.bytes[self.items_index..])?;
-
-            let previous_offset = self
-                .offsets
-                .last()
-                .map(|o| o.offset)
-                .unwrap_or_else(|| BYTES_PER_LENGTH_OFFSET);
-
-            if (previous_offset > offset) || (offset > self.bytes.len()) {
-                return Err(DecodeError::OutOfBoundsByte { i: offset });
-            }
-
             self.offsets.push(Offset {
                 position: self.items.len(),
-                offset,
+                offset: sanitize_offset(
+                    read_offset(&self.bytes[self.items_index..])?,
+                    self.offsets.last().map(|o| o.offset),
+                    self.bytes.len(),
+                    None,
+                )?,
             });
 
             // Push an empty slice into items; it will be replaced later.
@@ -124,13 +179,13 @@ impl<'a> SszDecoderBuilder<'a> {
     }
 
     fn finalize(&mut self) -> Result<(), DecodeError> {
-        if !self.offsets.is_empty() {
+        if let Some(first_offset) = self.offsets.first().map(|o| o.offset) {
             // Check to ensure the first offset points to the byte immediately following the
             // fixed-length bytes.
-            if self.offsets[0].offset != self.items_index {
-                return Err(DecodeError::OutOfBoundsByte {
-                    i: self.offsets[0].offset,
-                });
+            if first_offset < self.items_index {
+                return Err(DecodeError::OffsetIntoFixedPortion(first_offset));
+            } else if first_offset > self.items_index {
+                return Err(DecodeError::OffsetSkipsVariableBytes(first_offset));
             }
 
             // Iterate through each pair of offsets, grabbing the slice between each of the offsets.
```

### eth2/utils/ssz/src/decode/impls.rs
```diff
@@ -366,7 +366,7 @@ impl_decodable_for_u8_array!(4);
 impl_decodable_for_u8_array!(32);
 
 macro_rules! impl_for_vec {
-    ($type: ty) => {
+    ($type: ty, $max_len: expr) => {
         impl<T: Decode> Decode for $type {
             fn is_ssz_fixed_len() -> bool {
                 false
@@ -381,22 +381,22 @@ macro_rules! impl_for_vec {
                         .map(|chunk| T::from_ssz_bytes(chunk))
                         .collect()
                 } else {
-                    decode_list_of_variable_length_items(bytes).map(|vec| vec.into())
+                    decode_list_of_variable_length_items(bytes, $max_len).map(|vec| vec.into())
                 }
             }
         }
     };
 }
 
-impl_for_vec!(Vec<T>);
-impl_for_vec!(SmallVec<[T; 1]>);
-impl_for_vec!(SmallVec<[T; 2]>);
-impl_for_vec!(SmallVec<[T; 3]>);
-impl_for_vec!(SmallVec<[T; 4]>);
-impl_for_vec!(SmallVec<[T; 5]>);
-impl_for_vec!(SmallVec<[T; 6]>);
-impl_for_vec!(SmallVec<[T; 7]>);
-impl_for_vec!(SmallVec<[T; 8]>);
+impl_for_vec!(Vec<T>, None);
+impl_for_vec!(SmallVec<[T; 1]>, Some(1));
+impl_for_vec!(SmallVec<[T; 2]>, Some(2));
+impl_for_vec!(SmallVec<[T; 3]>, Some(3));
+impl_for_vec!(SmallVec<[T; 4]>, Some(4));
+impl_for_vec!(SmallVec<[T; 5]>, Some(5));
+impl_for_vec!(SmallVec<[T; 6]>, Some(6));
+impl_for_vec!(SmallVec<[T; 7]>, Some(7));
+impl_for_vec!(SmallVec<[T; 8]>, Some(8));
 
 /// Decodes `bytes` as if it were a list of variable-length items.
 ///
@@ -405,43 +405,52 @@ impl_for_vec!(SmallVec<[T; 8]>);
 /// differing types.
 pub fn decode_list_of_variable_length_items<T: Decode>(
     bytes: &[u8],
+    max_len: Option<usize>,
 ) -> Result<Vec<T>, DecodeError> {
-    let mut next_variable_byte = read_offset(bytes)?;
+    if bytes.is_empty() {
+        return Ok(vec![]);
+    }
+
+    let first_offset = read_offset(bytes)?;
+    sanitize_offset(first_offset, None, bytes.len(), Some(first_offset))?;
 
-    // The value of the first offset must not point back into the same bytes that defined
-    // it.
-    if next_variable_byte < BYTES_PER_LENGTH_OFFSET {
-        return Err(DecodeError::OutOfBoundsByte {
-            i: next_variable_byte,
-        });
+    if first_offset % BYTES_PER_LENGTH_OFFSET != 0 || first_offset < BYTES_PER_LENGTH_OFFSET {
+        return Err(DecodeError::InvalidListFixedBytesLen(first_offset));
     }
 
-    let num_items = next_variable_byte / BYTES_PER_LENGTH_OFFSET;
+    let num_items = first_offset / BYTES_PER_LENGTH_OFFSET;
 
-    // The fixed-length section must be a clean multiple of `BYTES_PER_LENGTH_OFFSET`.
-    if next_variable_byte != num_items * BYTES_PER_LENGTH_OFFSET {
-        return Err(DecodeError::InvalidByteLength {
-            len: next_variable_byte,
-            expected: num_items * BYTES_PER_LENGTH_OFFSET,
-        });
+    if max_len.map_or(false, |max| num_items > max) {
+        return Err(DecodeError::BytesInvalid(format!(
+            "Variable length list of {} items exceeds maximum of {:?}",
+            num_items, max_len
+        )));
     }
 
-    let mut values = Vec::with_capacity(num_items);
+    // Only initialize the vec with a capacity if a maximum length is provided.
+    //
+    // We assume that if a max length is provided then the application is able to handle an
+    // allocation of this size.
+    let mut values = if max_len.is_some() {
+        Vec::with_capacity(num_items)
+    } else {
+        vec![]
+    };
+
+    let mut offset = first_offset;
     for i in 1..=num_items {
         let slice_option = if i == num_items {
-            bytes.get(next_variable_byte..)
+            bytes.get(offset..)
         } else {
-            let offset = read_offset(&bytes[(i * BYTES_PER_LENGTH_OFFSET)..])?;
+            let start = offset;
 
-            let start = next_variable_byte;
-            next_variable_byte = offset;
+            let next_offset = read_offset(&bytes[(i * BYTES_PER_LENGTH_OFFSET)..])?;
+            offset = sanitize_offset(next_offset, Some(offset), bytes.len(), Some(first_offset))?;
 
-            bytes.get(start..next_variable_byte)
+            bytes.get(start..offset)
         };
 
-        let slice = slice_option.ok_or_else(|| DecodeError::OutOfBoundsByte {
-            i: next_variable_byte,
-        })?;
+        let slice = slice_option.ok_or_else(|| DecodeError::OutOfBoundsByte { i: offset })?;
 
         values.push(T::from_ssz_bytes(slice)?);
     }
@@ -519,60 +528,66 @@ mod tests {
         );
     }
 
+    #[test]
+    fn empty_list() {
+        let vec: Vec<Vec<u16>> = vec![];
+        let bytes = vec.as_ssz_bytes();
+        assert!(bytes.is_empty());
+        assert_eq!(Vec::from_ssz_bytes(&bytes), Ok(vec),);
+    }
+
     #[test]
     fn first_length_points_backwards() {
         assert_eq!(
             <Vec<Vec<u16>>>::from_ssz_bytes(&[0, 0, 0, 0]),
-            Err(DecodeError::OutOfBoundsByte { i: 0 })
+            Err(DecodeError::InvalidListFixedBytesLen(0))
         );
 
         assert_eq!(
             <Vec<Vec<u16>>>::from_ssz_bytes(&[1, 0, 0, 0]),
-            Err(DecodeError::OutOfBoundsByte { i: 1 })
+            Err(DecodeError::InvalidListFixedBytesLen(1))
         );
 
         assert_eq!(
             <Vec<Vec<u16>>>::from_ssz_bytes(&[2, 0, 0, 0]),
-            Err(DecodeError::OutOfBoundsByte { i: 2 })
+            Err(DecodeError::InvalidListFixedBytesLen(2))
         );
 
         assert_eq!(
             <Vec<Vec<u16>>>::from_ssz_bytes(&[3, 0, 0, 0]),
-            Err(DecodeError::OutOfBoundsByte { i: 3 })
+            Err(DecodeError::InvalidListFixedBytesLen(3))
         );
     }
 
     #[test]
     fn lengths_are_decreasing() {
         assert_eq!(
             <Vec<Vec<u16>>>::from_ssz_bytes(&[12, 0, 0, 0, 14, 0, 0, 0, 12, 0, 0, 0, 1, 0, 1, 0]),
-            Err(DecodeError::OutOfBoundsByte { i: 12 })
+            Err(DecodeError::OffsetsAreDecreasing(12))
         );
     }
 
     #[test]
     fn awkward_fixed_length_portion() {
         assert_eq!(
             <Vec<Vec<u16>>>::from_ssz_bytes(&[10, 0, 0, 0, 10, 0, 0, 0, 0, 0]),
-            Err(DecodeError::InvalidByteLength {
-                len: 10,
-                expected: 8
-            })
+            Err(DecodeError::InvalidListFixedBytesLen(10))
         );
     }
 
     #[test]
     fn length_out_of_bounds() {
         assert_eq!(
             <Vec<Vec<u16>>>::from_ssz_bytes(&[5, 0, 0, 0]),
-            Err(DecodeError::InvalidByteLength {
-                len: 5,
-                expected: 4
-            })
+            Err(DecodeError::OffsetOutOfBounds(5))
         );
         assert_eq!(
             <Vec<Vec<u16>>>::from_ssz_bytes(&[8, 0, 0, 0, 9, 0, 0, 0]),
-            Err(DecodeError::OutOfBoundsByte { i: 9 })
+            Err(DecodeError::OffsetOutOfBounds(9))
+        );
+        assert_eq!(
+            <Vec<Vec<u16>>>::from_ssz_bytes(&[8, 0, 0, 0, 16, 0, 0, 0]),
+            Err(DecodeError::OffsetOutOfBounds(16))
         );
     }
 
```

### eth2/utils/ssz/tests/tests.rs
```diff
@@ -152,7 +152,7 @@ mod round_trip {
 
         assert_eq!(
             VariableLen::from_ssz_bytes(&bytes),
-            Err(DecodeError::OutOfBoundsByte { i: 9 })
+            Err(DecodeError::OffsetIntoFixedPortion(9))
         );
     }
 
@@ -182,7 +182,7 @@ mod round_trip {
 
         assert_eq!(
             VariableLen::from_ssz_bytes(&bytes),
-            Err(DecodeError::OutOfBoundsByte { i: 11 })
+            Err(DecodeError::OffsetSkipsVariableBytes(11))
         );
     }
 
@@ -284,7 +284,7 @@ mod round_trip {
 
         assert_eq!(
             ThreeVariableLen::from_ssz_bytes(&bytes),
-            Err(DecodeError::OutOfBoundsByte { i: 14 })
+            Err(DecodeError::OffsetsAreDecreasing(14))
         );
     }
 
```

### eth2/utils/ssz_types/src/fixed_vector.rs
```diff
@@ -224,29 +224,44 @@ where
     }
 
     fn from_ssz_bytes(bytes: &[u8]) -> Result<Self, ssz::DecodeError> {
+        let fixed_len = N::to_usize();
+
         if bytes.is_empty() {
             Err(ssz::DecodeError::InvalidByteLength {
                 len: 0,
                 expected: 1,
             })
         } else if T::is_ssz_fixed_len() {
+            let num_items = bytes
+                .len()
+                .checked_div(T::ssz_fixed_len())
+                .ok_or_else(|| ssz::DecodeError::ZeroLengthItem)?;
+
+            if num_items != fixed_len {
+                return Err(ssz::DecodeError::BytesInvalid(format!(
+                    "FixedVector of {} items has {} items",
+                    num_items, fixed_len
+                )));
+            }
+
             bytes
                 .chunks(T::ssz_fixed_len())
                 .map(|chunk| T::from_ssz_bytes(chunk))
                 .collect::<Result<Vec<T>, _>>()
                 .and_then(|vec| {
-                    if vec.len() == N::to_usize() {
+                    if vec.len() == fixed_len {
                         Ok(vec.into())
                     } else {
                         Err(ssz::DecodeError::BytesInvalid(format!(
-                            "wrong number of vec elements, got: {}, expected: {}",
+                            "Wrong number of FixedVector elements, got: {}, expected: {}",
                             vec.len(),
                             N::to_usize()
                         )))
                     }
                 })
         } else {
-            ssz::decode_list_of_variable_length_items(bytes).and_then(|vec| Ok(vec.into()))
+            ssz::decode_list_of_variable_length_items(bytes, Some(fixed_len))
+                .and_then(|vec| Ok(vec.into()))
         }
     }
 }
```

### eth2/utils/ssz_types/src/variable_list.rs
```diff
@@ -218,22 +218,41 @@ where
     }
 }
 
-impl<T, N: Unsigned> ssz::Decode for VariableList<T, N>
+impl<T, N> ssz::Decode for VariableList<T, N>
 where
     T: ssz::Decode,
+    N: Unsigned,
 {
     fn is_ssz_fixed_len() -> bool {
-        <Vec<T>>::is_ssz_fixed_len()
-    }
-
-    fn ssz_fixed_len() -> usize {
-        <Vec<T>>::ssz_fixed_len()
+        false
     }
 
     fn from_ssz_bytes(bytes: &[u8]) -> Result<Self, ssz::DecodeError> {
-        let vec = <Vec<T>>::from_ssz_bytes(bytes)?;
-
-        Self::new(vec).map_err(|e| ssz::DecodeError::BytesInvalid(format!("VariableList {:?}", e)))
+        let max_len = N::to_usize();
+
+        if bytes.is_empty() {
+            Ok(vec![].into())
+        } else if T::is_ssz_fixed_len() {
+            let num_items = bytes
+                .len()
+                .checked_div(T::ssz_fixed_len())
+                .ok_or_else(|| ssz::DecodeError::ZeroLengthItem)?;
+
+            if num_items > max_len {
+                return Err(ssz::DecodeError::BytesInvalid(format!(
+                    "VariableList of {} items exceeds maximum of {}",
+                    num_items, max_len
+                )));
+            }
+
+            bytes
+                .chunks(T::ssz_fixed_len())
+                .map(|chunk| T::from_ssz_bytes(chunk))
+                .collect::<Result<Vec<_>, _>>()
+                .map(Into::into)
+        } else {
+            ssz::decode_list_of_variable_length_items(bytes, Some(max_len)).map(|vec| vec.into())
+        }
     }
 }
 
```

### lcli/src/helpers.rs
```diff
@@ -29,6 +29,14 @@ pub fn parse_path_with_default_in_home_dir(
         })
 }
 
+pub fn parse_path(matches: &ArgMatches, name: &'static str) -> Result<PathBuf, String> {
+    matches
+        .value_of(name)
+        .ok_or_else(|| format!("{} not specified", name))?
+        .parse::<PathBuf>()
+        .map_err(|e| format!("Unable to parse {}: {}", name, e))
+}
+
 pub fn parse_u64(matches: &ArgMatches, name: &'static str) -> Result<u64, String> {
     matches
         .value_of(name)
```

### lcli/src/main.rs
```diff
@@ -9,6 +9,7 @@ mod helpers;
 mod interop_genesis;
 mod new_testnet;
 mod parse_hex;
+mod parse_ssz;
 mod refund_deposit_contract;
 mod transition_blocks;
 
@@ -36,7 +37,6 @@ fn main() {
                 .long("spec")
                 .value_name("STRING")
                 .takes_value(true)
-                .required(true)
                 .possible_values(&["minimal", "mainnet"])
                 .default_value("mainnet")
         )
@@ -94,6 +94,27 @@ fn main() {
                         .help("Path to output a SSZ file."),
                 ),
         )
+        .subcommand(
+            SubCommand::with_name("pretty-ssz")
+                .about("Parses a file of raw (not hex-encoded) SSZ bytes")
+                .arg(
+                    Arg::with_name("type")
+                        .index(1)
+                        .value_name("TYPE")
+                        .takes_value(true)
+                        .required(true)
+                        .possible_values(&["SignedBeaconBlock"])
+                        .help("The schema of the supplied SSZ."),
+                )
+                .arg(
+                    Arg::with_name("path")
+                        .index(2)
+                        .value_name("SSZ_FILE")
+                        .takes_value(true)
+                        .required(true)
+                        .help("A file contains SSZ bytes"),
+                ),
+        )
         .subcommand(
             SubCommand::with_name("pretty-hex")
                 .about("Parses SSZ encoded as ASCII 0x-prefixed hex")
@@ -452,6 +473,14 @@ fn run<T: EthSpec>(env_builder: EnvironmentBuilder<T>, matches: &ArgMatches) {
         }
         ("transition-blocks", Some(matches)) => run_transition_blocks::<T>(matches)
             .unwrap_or_else(|e| error!("Failed to transition blocks: {}", e)),
+        ("pretty-ssz", Some(sub_matches)) => {
+            let result = match matches.value_of("spec").expect("spec is required by slog") {
+                "minimal" => parse_ssz::run::<MinimalEthSpec>(sub_matches),
+                "mainnet" => parse_ssz::run::<MainnetEthSpec>(sub_matches),
+                _ => unreachable!("guarded by slog possible_values"),
+            };
+            result.unwrap_or_else(|e| error!("Failed to run eth1-genesis command: {}", e))
+        }
         ("pretty-hex", Some(matches)) => run_parse_hex::<T>(matches)
             .unwrap_or_else(|e| error!("Failed to pretty print hex: {}", e)),
         ("deploy-deposit-contract", Some(matches)) => {
```

### lcli/src/parse_ssz.rs
```diff
@@ -0,0 +1,40 @@
+use crate::helpers::parse_path;
+use clap::ArgMatches;
+use serde::Serialize;
+use ssz::Decode;
+use std::fs::File;
+use std::io::Read;
+use types::{EthSpec, SignedBeaconBlock};
+
+pub fn run<T: EthSpec>(matches: &ArgMatches) -> Result<(), String> {
+    let type_str = matches
+        .value_of("type")
+        .ok_or_else(|| "No type supplied".to_string())?;
+    let path = parse_path(matches, "path")?;
+
+    info!("Type: {:?}", type_str);
+
+    let mut bytes = vec![];
+    let mut file = File::open(&path).map_err(|e| format!("Unable to open {:?}: {}", path, e))?;
+    file.read_to_end(&mut bytes)
+        .map_err(|e| format!("Unable to read {:?}: {}", path, e))?;
+
+    match type_str {
+        "SignedBeaconBlock" => decode_and_print::<SignedBeaconBlock<T>>(&bytes)?,
+        other => return Err(format!("Unknown type: {}", other)),
+    };
+
+    Ok(())
+}
+
+fn decode_and_print<T: Decode + Serialize>(bytes: &[u8]) -> Result<(), String> {
+    let item = T::from_ssz_bytes(&bytes).map_err(|e| format!("Ssz decode failed: {:?}", e))?;
+
+    println!(
+        "{}",
+        serde_yaml::to_string(&item)
+            .map_err(|e| format!("Unable to write object to YAML: {:?}", e))?
+    );
+
+    Ok(())
+}
```
