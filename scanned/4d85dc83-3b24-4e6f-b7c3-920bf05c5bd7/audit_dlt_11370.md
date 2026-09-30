# [?] fix: return error rather than panicking on unreadable circuits (#3179)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-10-17
Source: https://github.com/noir-lang/noir/commit/d4f61d3d51d515e40a5fd02d35315889f841bf53
Type: security-commit

## Details
fix: return error rather than panicking on unreadable circuits (#3179)

## Patch
### acvm-repo/acir/src/circuit/mod.rs
```diff
@@ -128,17 +128,17 @@ impl Circuit {
     pub fn write<W: std::io::Write>(&self, writer: W) -> std::io::Result<()> {
         let buf = bincode::serialize(self).unwrap();
         let mut encoder = flate2::write::GzEncoder::new(writer, Compression::default());
-        encoder.write_all(&buf).unwrap();
-        encoder.finish().unwrap();
+        encoder.write_all(&buf)?;
+        encoder.finish()?;
         Ok(())
     }
 
     pub fn read<R: std::io::Read>(reader: R) -> std::io::Result<Self> {
         let mut gz_decoder = flate2::read::GzDecoder::new(reader);
         let mut buf_d = Vec::new();
-        gz_decoder.read_to_end(&mut buf_d).unwrap();
-        let circuit = bincode::deserialize(&buf_d).unwrap();
-        Ok(circuit)
+        gz_decoder.read_to_end(&mut buf_d)?;
+        bincode::deserialize(&buf_d)
+            .map_err(|err| std::io::Error::new(std::io::ErrorKind::InvalidInput, err))
     }
 }
 
@@ -199,7 +199,7 @@ mod tests {
 
     use super::{
         opcodes::{BlackBoxFuncCall, FunctionInput},
-        Circuit, Opcode, PublicInputs,
+        Circuit, Compression, Opcode, PublicInputs,
     };
     use crate::native_types::Witness;
     use acir_field::FieldElement;
@@ -263,4 +263,21 @@ mod tests {
         let deserialized = serde_json::from_str(&json).unwrap();
         assert_eq!(circuit, deserialized);
     }
+
+    #[test]
+    fn does_not_panic_on_invalid_circuit() {
+        use std::io::Write;
+
+        let bad_circuit = "I'm not an ACIR circuit".as_bytes();
+
+        // We expect to load circuits as compressed artifacts so we compress the junk circuit.
+        let mut zipped_bad_circuit = Vec::new();
+        let mut encoder =
+            flate2::write::GzEncoder::new(&mut zipped_bad_circuit, Compression::default());
+        encoder.write_all(bad_circuit).unwrap();
+        encoder.finish().unwrap();
+
+        let deserialization_result = Circuit::read(&*zipped_bad_circuit);
+        assert!(deserialization_result.is_err());
+    }
 }
```

### compiler/noirc_driver/src/program.rs
```diff
@@ -5,6 +5,7 @@ use fm::FileId;
 
 use base64::Engine;
 use noirc_errors::debug_info::DebugInfo;
+use serde::{de::Error as DeserializationError, ser::Error as SerializationError};
 use serde::{Deserialize, Deserializer, Serialize, Serializer};
 
 use super::debug::DebugFile;
@@ -29,7 +30,7 @@ where
     S: Serializer,
 {
     let mut circuit_bytes: Vec<u8> = Vec::new();
-    circuit.write(&mut circuit_bytes).unwrap();
+    circuit.write(&mut circuit_bytes).map_err(S::Error::custom)?;
 
     let encoded_b64 = base64::engine::general_purpose::STANDARD.encode(circuit_bytes);
     s.serialize_str(&encoded_b64)
@@ -40,7 +41,8 @@ where
     D: Deserializer<'de>,
 {
     let bytecode_b64: String = serde::Deserialize::deserialize(deserializer)?;
-    let circuit_bytes = base64::engine::general_purpose::STANDARD.decode(bytecode_b64).unwrap();
-    let circuit = Circuit::read(&*circuit_bytes).unwrap();
+    let circuit_bytes =
+        base64::engine::general_purpose::STANDARD.decode(bytecode_b64).map_err(D::Error::custom)?;
+    let circuit = Circuit::read(&*circuit_bytes).map_err(D::Error::custom)?;
     Ok(circuit)
 }
```

### tooling/nargo/src/artifacts/mod.rs
```diff
@@ -5,7 +5,9 @@
 //! to generate them using these artifacts as a starting point.
 use acvm::acir::circuit::Circuit;
 use base64::Engine;
-use serde::{Deserializer, Serializer};
+use serde::{
+    de::Error as DeserializationError, ser::Error as SerializationError, Deserializer, Serializer,
+};
 
 pub mod contract;
 pub mod debug;
@@ -17,7 +19,7 @@ where
     S: Serializer,
 {
     let mut circuit_bytes: Vec<u8> = Vec::new();
-    circuit.write(&mut circuit_bytes).unwrap();
+    circuit.write(&mut circuit_bytes).map_err(S::Error::custom)?;
     let encoded_b64 = base64::engine::general_purpose::STANDARD.encode(circuit_bytes);
     s.serialize_str(&encoded_b64)
 }
@@ -27,7 +29,8 @@ where
     D: Deserializer<'de>,
 {
     let bytecode_b64: String = serde::Deserialize::deserialize(deserializer)?;
-    let circuit_bytes = base64::engine::general_purpose::STANDARD.decode(bytecode_b64).unwrap();
-    let circuit = Circuit::read(&*circuit_bytes).unwrap();
+    let circuit_bytes =
+        base64::engine::general_purpose::STANDARD.decode(bytecode_b64).map_err(D::Error::custom)?;
+    let circuit = Circuit::read(&*circuit_bytes).map_err(D::Error::custom)?;
     Ok(circuit)
 }
```
