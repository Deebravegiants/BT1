# [?] fix(cast): avoid stack overflow on nested RLP (#16233)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-08-18
Source: https://github.com/foundry-rs/foundry/commit/dce9d1d8721b9fa1c97ccc781994617f35a6e6f7
Type: security-commit

## Details
fix(cast): avoid stack overflow on nested RLP (#16233)

## Patch
### .changelog/cast-deeply-nested-rlp.md
```diff
@@ -0,0 +1,5 @@
+---
+cast: patch
+---
+
+Prevented `cast from-rlp` from overflowing the stack on deeply nested RLP lists.
```

### crates/cast/src/rlp_converter.rs
```diff
@@ -1,5 +1,5 @@
 use alloy_primitives::{U256, hex};
-use alloy_rlp::{Buf, Decodable, Encodable, Header};
+use alloy_rlp::{Decodable, Encodable, Header, PayloadView};
 use eyre::Context;
 use serde_json::Value;
 use std::fmt;
@@ -25,23 +25,50 @@ impl Encodable for Item {
 
 impl Decodable for Item {
     fn decode(buf: &mut &[u8]) -> alloy_rlp::Result<Self> {
-        let h = Header::decode(buf)?;
-        if buf.len() < h.payload_length {
-            return Err(alloy_rlp::Error::InputTooShort);
+        struct ListFrame<'a> {
+            remaining: std::vec::IntoIter<&'a [u8]>,
+            items: Vec<Item>,
         }
-        let mut d = &buf[..h.payload_length];
-        let r = if h.list {
-            let view = &mut d;
-            let mut v = Vec::new();
-            while !view.is_empty() {
-                v.push(Self::decode(view)?);
-            }
-            Ok(Self::Array(v))
-        } else {
-            Ok(Self::Data(d.to_vec()))
+
+        let items = match Header::decode_raw(buf)? {
+            PayloadView::String(data) => return Ok(Self::Data(data.to_vec())),
+            PayloadView::List(items) => items,
         };
-        buf.advance(h.payload_length);
-        r
+
+        let mut frames = vec![ListFrame { remaining: items.into_iter(), items: Vec::new() }];
+        loop {
+            let Some(encoded) = frames.last_mut().unwrap().remaining.next() else {
+                let frame = frames.pop().unwrap();
+                let item = Self::Array(frame.items);
+                if let Some(parent) = frames.last_mut() {
+                    parent.items.push(item);
+                    continue;
+                }
+                return Ok(item);
+            };
+
+            match Header::decode_raw(&mut &encoded[..])? {
+                PayloadView::String(data) => {
+                    frames.last_mut().unwrap().items.push(Self::Data(data.to_vec()));
+                }
+                PayloadView::List(items) => {
+                    frames.push(ListFrame { remaining: items.into_iter(), items: Vec::new() });
+                }
+            }
+        }
+    }
+}
+
+impl Drop for Item {
+    fn drop(&mut self) {
+        // The default recursive drop can overflow after successfully decoding deeply nested RLP.
+        let Self::Array(items) = self else { return };
+        let mut pending = std::mem::take(items);
+        while let Some(mut item) = pending.pop() {
+            if let Self::Array(children) = &mut item {
+                pending.append(children);
+            }
+        }
     }
 }
 
@@ -73,21 +100,30 @@ impl FromIterator<Self> for Item {
 // Display as hex values
 impl fmt::Display for Item {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> std::fmt::Result {
-        match self {
-            Self::Data(dat) => {
-                write!(f, "\"0x{}\"", hex::encode(dat))?;
-            }
-            Self::Array(items) => {
-                f.write_str("[")?;
-                for (i, item) in items.iter().enumerate() {
-                    if i > 0 {
-                        f.write_str(",")?;
+        enum Task<'a> {
+            Item(&'a Item),
+            Comma,
+            Close,
+        }
+
+        let mut tasks = vec![Task::Item(self)];
+        while let Some(task) = tasks.pop() {
+            match task {
+                Task::Item(Self::Data(data)) => write!(f, "\"0x{}\"", hex::encode(data))?,
+                Task::Item(Self::Array(items)) => {
+                    f.write_str("[")?;
+                    tasks.push(Task::Close);
+                    for (i, item) in items.iter().enumerate().rev() {
+                        tasks.push(Task::Item(item));
+                        if i > 0 {
+                            tasks.push(Task::Comma);
+                        }
                     }
-                    fmt::Display::fmt(item, f)?;
                 }
-                f.write_str("]")?;
+                Task::Comma => f.write_str(",")?,
+                Task::Close => f.write_str("]")?,
             }
-        };
+        }
         Ok(())
     }
 }
```

### crates/cast/tests/cli/main.rs
```diff
@@ -6,6 +6,7 @@ use alloy_hardforks::EthereumHardfork;
 use alloy_network::{ReceiptResponse, TransactionBuilder, TransactionResponse};
 use alloy_primitives::{Address, B256, Bytes, I256, U256, address, b256, hex, keccak256};
 use alloy_provider::{Provider, ProviderBuilder};
+use alloy_rlp::Header;
 use alloy_rpc_types::{
     Authorization, BlockNumberOrTag, Index, TransactionRequest, engine::JwtSecret,
 };
@@ -2847,6 +2848,24 @@ casttest!(rlp, |_prj, cmd| {
 [["0x55556666"],[],[],[[[]]]]
 
 "#]]);
+
+    // Build the RLP encoding of 10,000 nested single-item lists without recursively encoding it.
+    const NESTING_DEPTH: usize = 10_000;
+    let mut encoded_len = 1;
+    let mut headers = Vec::with_capacity(NESTING_DEPTH);
+    for _ in 0..NESTING_DEPTH {
+        let mut header = Vec::new();
+        Header { list: true, payload_length: encoded_len }.encode(&mut header);
+        encoded_len += header.len();
+        headers.push(header);
+    }
+    let mut deeply_nested = Vec::with_capacity(encoded_len);
+    for header in headers.iter().rev() {
+        deeply_nested.extend_from_slice(header);
+    }
+    deeply_nested.push(0x80);
+
+    cmd.cast_fuse().arg("--from-rlp").stdin(hex::encode_prefixed(deeply_nested)).assert_success();
 });
 
 // test that `cast impl` works correctly for both the implementation slot and the beacon slot
```
