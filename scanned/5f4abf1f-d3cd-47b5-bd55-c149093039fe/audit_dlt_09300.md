# [?] Fix panic on NaN/Inf values in TOML to JSON conversion (#11574)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-09-08
Source: https://github.com/foundry-rs/foundry/commit/79140e963bac2a7ac86df915ec7f281e196281a4
Type: security-commit

## Details
Fix panic on NaN/Inf values in TOML to JSON conversion (#11574)

* Update toml.rs

* Update test.toml

* Update Toml.t.sol

* Update test.toml

* Update Toml.t.sol

## Patch
### crates/cheatcodes/src/toml.rs
```diff
@@ -234,7 +234,10 @@ pub(super) fn toml_to_json_value(toml: TomlValue) -> JsonValue {
             _ => JsonValue::String(s),
         },
         TomlValue::Integer(i) => JsonValue::Number(i.into()),
-        TomlValue::Float(f) => JsonValue::Number(serde_json::Number::from_f64(f).unwrap()),
+        TomlValue::Float(f) => match serde_json::Number::from_f64(f) {
+            Some(n) => JsonValue::Number(n),
+            None => JsonValue::String(f.to_string()),
+        },
         TomlValue::Boolean(b) => JsonValue::Bool(b),
         TomlValue::Array(a) => JsonValue::Array(a.into_iter().map(toml_to_json_value).collect()),
         TomlValue::Table(t) => {
```

### testdata/default/cheats/Toml.t.sol
```diff
@@ -329,6 +329,24 @@ contract ParseTomlTest is DSTest {
 
         assertEq(keccak256(abi.encode(members)), keccak256(abi.encode(data.members)));
     }
+
+    function test_floatNaN() public {
+        bytes memory data = vm.parseToml(toml, ".nanFloat");
+        string memory decodedData = abi.decode(data, (string));
+        assertEq("NaN", decodedData);
+    }
+
+    function test_floatInf() public {
+        bytes memory data = vm.parseToml(toml, ".infFloat");
+        string memory decodedData = abi.decode(data, (string));
+        assertEq("inf", decodedData);
+    }
+
+    function test_floatNegInf() public {
+        bytes memory data = vm.parseToml(toml, ".neginfFloat");
+        string memory decodedData = abi.decode(data, (string));
+        assertEq("-inf", decodedData);
+    }
 }
 
 contract WriteTomlTest is DSTest {
```

### testdata/fixtures/Toml/test.toml
```diff
@@ -1,3 +1,7 @@
+nanFloat = nan
+infFloat = +inf
+neginfFloat = -inf
+
 basicString = "hai"
 nullString = "null"
 multilineString = """
@@ -48,3 +52,5 @@ id = 1
 
 [[advancedTomlPath]]
 id = 2
+
+
```
