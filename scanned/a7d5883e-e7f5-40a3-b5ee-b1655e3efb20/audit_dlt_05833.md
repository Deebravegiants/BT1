# [?] Fix unsoundness in RawVal::get_tag (#773)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2023-04-29
Source: https://github.com/stellar/rs-soroban-env/commit/e5cdfd871093e002428f924162152df248a0e22b
Type: security-commit

## Details
Fix unsoundness in RawVal::get_tag (#773)

* Remove gaps from Tag discriminants

* Update test wasms

Built with sdk commit 9383a6ae6f21c24cfe74a53759949b2c83d53e78

* Extract Tag::from_u8 from RawVal::get_tag

* Add test for Tag::from_u8

---------

Co-authored-by: Graydon Hoare <graydon@pobox.com>

## Patch
### Cargo.lock
```diff
@@ -584,6 +584,27 @@ version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8e04e2fd2b8188ea827b32ef11de88377086d690286ab35747ef7f9bf3ccb590"
 
+[[package]]
+name = "int-enum"
+version = "0.5.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "cff87d3cc4b79b4559e3c75068d64247284aceb6a038bd4bb38387f3f164476d"
+dependencies = [
+ "int-enum-impl",
+]
+
+[[package]]
+name = "int-enum-impl"
+version = "0.5.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "df1f2f068675add1a3fc77f5f5ab2e29290c841ee34d151abc007bce902e5d34"
+dependencies = [
+ "proc-macro-crate",
+ "proc-macro2",
+ "quote",
+ "syn",
+]
+
 [[package]]
 name = "itertools"
 version = "0.10.5"
@@ -867,6 +888,16 @@ version = "0.2.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "eb9f9e6e233e5c4a35559a617bf40a4ec447db2e84c20b55a6f83167b7e57872"
 
+[[package]]
+name = "proc-macro-crate"
+version = "1.3.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7f4c021e1093a56626774e81216a4ce732a735e5bad4868a03f3ed65ca0c3919"
+dependencies = [
+ "once_cell",
+ "toml_edit",
+]
+
 [[package]]
 name = "proc-macro-error"
 version = "1.0.4"
@@ -1118,6 +1149,7 @@ dependencies = [
  "arbitrary",
  "crate-git-revision",
  "ethnum",
+ "int-enum",
  "serde",
  "soroban-env-macros",
  "soroban-wasmi",
@@ -1435,6 +1467,23 @@ version = "0.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cda74da7e1a664f795bb1f8a87ec406fb89a02522cf6e50620d016add6dbbf5c"
 
+[[package]]
+name = "toml_datetime"
+version = "0.6.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "3ab8ed2edee10b50132aed5f331333428b011c99402b5a534154ed15746f9622"
+
+[[package]]
+name = "toml_edit"
+version = "0.19.8"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "239410c8609e8125456927e6707163a3b1fdb40561e4b803bc041f466ccfdc13"
+dependencies = [
+ "indexmap",
+ "toml_datetime",
+ "winnow",
+]
+
 [[package]]
 name = "tracing"
 version = "0.1.36"
@@ -1654,6 +1703,15 @@ version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "712e227841d057c1ee1cd2fb22fa7e5a5461ae8e48fa2ca79ec42cfc1931183f"
 
+[[package]]
+name = "winnow"
+version = "0.4.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ae8970b36c66498d8ff1d66685dc86b91b29db0c7739899012f63a63814b4b28"
+dependencies = [
+ "memchr",
+]
+
 [[package]]
 name = "zeroize"
 version = "1.3.0"
```

### soroban-env-common/Cargo.toml
```diff
@@ -22,6 +22,9 @@ static_assertions = "1.1.0"
 ethnum = "1.3.2"
 arbitrary = { version = "1.1.3", features = ["derive"], optional = true }
 
+[dev-dependencies]
+int-enum = "0.5.0"
+
 [features]
 std = ["stellar-xdr/std", "stellar-xdr/base64"]
 serde = ["dep:serde", "stellar-xdr/serde"]
```

### soroban-env-common/src/raw_val.rs
```diff
@@ -42,6 +42,7 @@ sa::const_assert!(MAJOR_BITS + MINOR_BITS == BODY_BITS);
 /// special cases (boolean true and false, small-value forms).
 #[repr(u8)]
 #[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Debug)]
+#[cfg_attr(test, derive(int_enum::IntEnum))]
 pub enum Tag {
     /// Tag for a [RawVal] that encodes [bool] `false`. The bool type is refined to
     /// two single-value subtypes in order for each tag number to coincides with
@@ -132,21 +133,21 @@ pub enum Tag {
     I256Object = 71,
 
     BytesObject = 72,
-    StringObject = 74,
-    SymbolObject = 75,
+    StringObject = 73,
+    SymbolObject = 74,
 
-    VecObject = 77,
-    MapObject = 78,
+    VecObject = 75,
+    MapObject = 76,
 
-    ContractExecutableObject = 79,
-    AddressObject = 80,
+    ContractExecutableObject = 77,
+    AddressObject = 78,
 
     /// Tag for a [RawVal] that corresponds to
     /// [stellar_xdr::ScVal::LedgerKeyNonce] and refers to a host-side
     /// address object that specifies which address it's the nonce for.
-    LedgerKeyNonceObject = 81,
+    LedgerKeyNonceObject = 79,
 
-    ObjectCodeUpperBound = 82,
+    ObjectCodeUpperBound = 80,
 
     Bad = 0x7f,
 }
@@ -162,6 +163,26 @@ impl Tag {
         let tu8 = self as u8;
         tu8 > (Tag::ObjectCodeLowerBound as u8) || tu8 < (Tag::ObjectCodeUpperBound as u8)
     }
+
+    #[inline(always)]
+    pub const fn from_u8(tag: u8) -> Tag {
+        const A: u8 = Tag::SmallCodeUpperBound as u8;
+        const B: u8 = Tag::ObjectCodeLowerBound as u8;
+        const C: u8 = Tag::ObjectCodeUpperBound as u8;
+        if !((tag < A) || (B < tag && tag < C)) {
+            return Tag::Bad;
+        }
+
+        // Transmuting an integer to an enum is UB if outside the defined enum
+        // value set, so we need to test above to be safe. Note that it's ok for
+        // this to be a _little_ slow since it's not called in a lot
+        // of small/tight paths, only when doing a switch-based comparison. Most
+        // small paths call `has_tag` which tests a _known_ enum case against
+        // the tag byte, and therefore doesn't need the range check.
+        //
+        // The `test_tag_from_u8` test should ensure this cast is correct.
+        unsafe { ::core::mem::transmute(tag) }
+    }
 }
 
 #[repr(transparent)]
@@ -498,19 +519,7 @@ impl RawVal {
     #[inline(always)]
     pub const fn get_tag(self) -> Tag {
         let tag = self.get_tag_u8();
-        const A: u8 = Tag::SmallCodeUpperBound as u8;
-        const B: u8 = Tag::ObjectCodeLowerBound as u8;
-        const C: u8 = Tag::ObjectCodeUpperBound as u8;
-        if !((tag < A) || (B < tag && tag < C)) {
-            return Tag::Bad;
-        }
-        // Transmuting an integer to an enum is UB if outside the defined enum
-        // value set, so we need to test above to be safe. Note that it's ok for
-        // `get_tag` here to be a _little_ slow since it's not called in a lot
-        // of small/tight paths, only when doing a switch-based comparison. Most
-        // small paths call `has_tag` which tests a _known_ enum case against
-        // the tag byte, and therefore doesn't need the range check.
-        unsafe { ::core::mem::transmute(tag) }
+        Tag::from_u8(tag)
     }
 
     #[inline(always)]
@@ -719,3 +728,33 @@ fn test_debug() {
         "Status(HostValueError(ReservedTagValue))"
     );
 }
+
+// `Tag::from_u8` is implemented by hand unsafely.
+//
+// This test ensures that all cases are correct by comparing to the
+// macro-generated results of the int-enum crate, which is only enabled as a
+// dev-dependency.
+#[test]
+fn test_tag_from_u8() {
+    use int_enum::IntEnum;
+
+    for i in 0_u8..=255 {
+        let expected_tag = Tag::from_int(i);
+        let actual_tag = Tag::from_u8(i);
+        match expected_tag {
+            Ok(Tag::SmallCodeUpperBound)
+            | Ok(Tag::ObjectCodeLowerBound)
+            | Ok(Tag::ObjectCodeUpperBound) => {
+                assert_eq!(actual_tag, Tag::Bad);
+            }
+            Ok(expected_tag) => {
+                assert_eq!(expected_tag, actual_tag);
+                let i_again = actual_tag as u8;
+                assert_eq!(i, i_again);
+            }
+            Err(_) => {
+                assert_eq!(actual_tag, Tag::Bad);
+            }
+        }
+    }
+}
```

### soroban-test-wasms/wasm-workspace/Cargo.lock
```diff
@@ -928,7 +928,7 @@ dependencies = [
  "soroban-env-macros",
  "soroban-wasmi",
  "static_assertions",
- "stellar-xdr 0.0.15 (git+https://github.com/stellar/rs-stellar-xdr?rev=48052d83db7f577164264d916b8590d792a67b02)",
+ "stellar-xdr 0.0.15 (git+https://github.com/stellar/rs-stellar-xdr?rev=2302358949c88e6e7529ee46947e41212e6de3b1)",
 ]
 
 [[package]]
@@ -969,7 +969,7 @@ dependencies = [
  "quote",
  "serde",
  "serde_json",
- "stellar-xdr 0.0.15 (git+https://github.com/stellar/rs-stellar-xdr?rev=48052d83db7f577164264d916b8590d792a67b02)",
+ "stellar-xdr 0.0.15 (git+https://github.com/stellar/rs-stellar-xdr?rev=2302358949c88e6e7529ee46947e41212e6de3b1)",
  "syn",
  "thiserror",
 ]
@@ -1089,7 +1089,7 @@ dependencies = [
 [[package]]
 name = "stellar-xdr"
 version = "0.0.15"
-source = "git+https://github.com/stellar/rs-stellar-xdr?rev=48052d83db7f577164264d916b8590d792a67b02#48052d83db7f577164264d916b8590d792a67b02"
+source = "git+https://github.com/stellar/rs-stellar-xdr?rev=2302358949c88e6e7529ee46947e41212e6de3b1#2302358949c88e6e7529ee46947e41212e6de3b1"
 dependencies = [
  "arbitrary",
  "base64",
```
