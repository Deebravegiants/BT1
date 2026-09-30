# [?] fix: don't panic on ABI tuple length mismatch (#12096)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-04-03
Source: https://github.com/noir-lang/noir/commit/4b1d34b7d5adaf58e679803ee805221209ac2606
Type: security-commit

## Details
fix: don't panic on ABI tuple length mismatch (#12096)

## Patch
### tooling/noirc_abi/src/input_parser/json.rs
```diff
@@ -5,7 +5,6 @@ use super::{
 use crate::{Abi, AbiType, MAIN_RETURN_NAME, errors::InputParserError};
 use acvm::{AcirField, FieldElement};
 use iter_extended::{try_btree_map, try_vecmap};
-use itertools::Itertools;
 use serde::{Deserialize, Serialize};
 use std::collections::BTreeMap;
 
@@ -115,7 +114,7 @@ impl JsonTypes {
             }
 
             (InputValue::Vec(vector), AbiType::Tuple { fields }) => {
-                let fields = try_vecmap(vector.iter().zip_eq(fields), |(value, typ)| {
+                let fields = try_vecmap(vector.iter().zip(fields), |(value, typ)| {
                     JsonTypes::try_from_input_value(value, typ)
                 })?;
                 JsonTypes::Array(fields)
@@ -209,7 +208,7 @@ impl InputValue {
 
             (JsonTypes::Array(array), AbiType::Tuple { fields }) => {
                 let mut index = 0;
-                let tuple_fields = try_vecmap(array.into_iter().zip_eq(fields), |(value, typ)| {
+                let tuple_fields = try_vecmap(array.into_iter().zip(fields), |(value, typ)| {
                     let sub_name = format!("{arg_name}[{index}]");
                     let value = InputValue::try_from_json(value, typ, &sub_name);
                     index += 1;
@@ -236,7 +235,7 @@ mod tests {
     use proptest::prelude::*;
 
     use crate::{
-        AbiType,
+        Abi, AbiParameter, AbiType, AbiVisibility,
         arbitrary::arb_abi_and_input_map,
         input_parser::{InputValue, arbitrary::arb_signed_integer_type_and_value, json::JsonTypes},
     };
@@ -289,4 +288,30 @@ mod tests {
         };
         assert_eq!(field, FieldElement::from(255_u128));
     }
+
+    #[test]
+    fn try_from_json_tuple_array_length_mismatch() {
+        let typ = AbiType::Tuple { fields: vec![AbiType::Field, AbiType::Field] };
+        let abi = Abi {
+            parameters: vec![AbiParameter {
+                name: "input".to_string(),
+                typ,
+                visibility: AbiVisibility::Private,
+            }],
+            return_type: None,
+            error_types: Default::default(),
+        };
+        let json = r#"{"input": [0]}"#;
+        let input = parse_json(json, &abi).unwrap();
+        let value = &input["input"];
+        assert!(matches!(value, InputValue::Vec(vec) if vec.len() == 1));
+    }
+
+    #[test]
+    fn try_from_input_value_toml_array_length_mismatch() {
+        let value = InputValue::Vec(vec![InputValue::Field(0.into())]);
+        let abi_type = AbiType::Tuple { fields: vec![AbiType::Field, AbiType::Field] };
+        let result = JsonTypes::try_from_input_value(&value, &abi_type).unwrap();
+        assert!(matches!(result, JsonTypes::Array(array) if array.len() == 1));
+    }
 }
```

### tooling/noirc_abi/src/input_parser/toml.rs
```diff
@@ -5,7 +5,6 @@ use super::{
 use crate::{Abi, AbiType, MAIN_RETURN_NAME, errors::InputParserError};
 use acvm::{AcirField, FieldElement};
 use iter_extended::{try_btree_map, try_vecmap};
-use itertools::Itertools;
 use serde::{Deserialize, Serialize, de::Error};
 use std::collections::BTreeMap;
 
@@ -122,7 +121,7 @@ impl TomlTypes {
             }
 
             (InputValue::Vec(vector), AbiType::Tuple { fields }) => {
-                let fields = try_vecmap(vector.iter().zip_eq(fields), |(value, typ)| {
+                let fields = try_vecmap(vector.iter().zip(fields), |(value, typ)| {
                     TomlTypes::try_from_input_value(value, typ)
                 })?;
                 TomlTypes::Array(fields)
@@ -203,7 +202,7 @@ impl InputValue {
 
             (TomlTypes::Array(array), AbiType::Tuple { fields }) => {
                 let mut index = 0;
-                let tuple_fields = try_vecmap(array.into_iter().zip_eq(fields), |(value, typ)| {
+                let tuple_fields = try_vecmap(array.into_iter().zip(fields), |(value, typ)| {
                     let sub_name = format!("{arg_name}[{index}]");
                     let value = InputValue::try_from_toml(value, typ, &sub_name);
                     index += 1;
@@ -317,4 +316,30 @@ mod tests {
         let err = parse_toml(toml, &abi).unwrap_err();
         assert!(err.to_string().contains("note: large Field numbers can be written by wrapping them in double quotes (that is, using strings)"));
     }
+
+    #[test]
+    fn try_from_toml_tuple_array_length_mismatch() {
+        let typ = AbiType::Tuple { fields: vec![AbiType::Field, AbiType::Field] };
+        let abi = Abi {
+            parameters: vec![AbiParameter {
+                name: "input".to_string(),
+                typ,
+                visibility: AbiVisibility::Private,
+            }],
+            return_type: None,
+            error_types: Default::default(),
+        };
+        let toml = "input = [0]";
+        let input = parse_toml(toml, &abi).unwrap();
+        let value = &input["input"];
+        assert!(matches!(value, InputValue::Vec(vec) if vec.len() == 1));
+    }
+
+    #[test]
+    fn try_from_input_value_toml_array_length_mismatch() {
+        let value = InputValue::Vec(vec![InputValue::Field(0.into())]);
+        let abi_type = AbiType::Tuple { fields: vec![AbiType::Field, AbiType::Field] };
+        let result = TomlTypes::try_from_input_value(&value, &abi_type).unwrap();
+        assert!(matches!(result, TomlTypes::Array(array) if array.len() == 1));
+    }
 }
```
