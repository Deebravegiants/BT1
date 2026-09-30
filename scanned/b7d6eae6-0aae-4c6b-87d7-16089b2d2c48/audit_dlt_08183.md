# [?] Stop panicking when Zebra sends a reject without extra data

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2021-04-15
Source: https://github.com/ZcashFoundation/zebra/commit/59aa04c9b99fd0ca91b07122d2816465323a94ab
Type: security-commit

## Details
Stop panicking when Zebra sends a reject without extra data

Also add round-trip unit tests for extra data and no extra data.

## Patch
### zebra-network/src/protocol/external/codec.rs
```diff
@@ -251,7 +251,9 @@ impl Codec {
                 writer.write_string(&message)?;
                 writer.write_u8(*ccode as u8)?;
                 writer.write_string(&reason)?;
-                writer.write_all(&data.unwrap())?;
+                if let Some(data) = data {
+                    writer.write_all(data)?;
+                }
             }
             Message::Addr(addrs) => addrs.zcash_serialize(&mut writer)?,
             Message::GetAddr => { /* Empty payload -- no-op */ }
@@ -511,7 +513,8 @@ impl Codec {
             // data (hash identifying the rejected object) or none (and we model
             // the Reject message that way), so instead of passing in the
             // body_len separately and calculating remaining bytes, just try to
-            // read 32 bytes and ignore any failures.
+            // read 32 bytes and ignore any failures. (The caller will log and
+            // ignore any trailing bytes.)
             data: reader.read_32_bytes().ok(),
         })
     }
@@ -720,6 +723,78 @@ mod tests {
         assert_eq!(v, v_parsed);
     }
 
+    #[test]
+    fn reject_message_no_extra_data_round_trip() {
+        zebra_test::init();
+
+        let rt = Runtime::new().unwrap();
+
+        let v = Message::Reject {
+            message: "experimental".to_string(),
+            ccode: RejectReason::Malformed,
+            reason: "message could not be decoded".to_string(),
+            data: None,
+        };
+
+        use tokio_util::codec::{FramedRead, FramedWrite};
+        let v_bytes = rt.block_on(async {
+            let mut bytes = Vec::new();
+            {
+                let mut fw = FramedWrite::new(&mut bytes, Codec::builder().finish());
+                fw.send(v.clone())
+                    .await
+                    .expect("message should be serialized");
+            }
+            bytes
+        });
+
+        let v_parsed = rt.block_on(async {
+            let mut fr = FramedRead::new(Cursor::new(&v_bytes), Codec::builder().finish());
+            fr.next()
+                .await
+                .expect("a next message should be available")
+                .expect("that message should deserialize")
+        });
+
+        assert_eq!(v, v_parsed);
+    }
+
+    #[test]
+    fn reject_message_extra_data_round_trip() {
+        zebra_test::init();
+
+        let rt = Runtime::new().unwrap();
+
+        let v = Message::Reject {
+            message: "block".to_string(),
+            ccode: RejectReason::Invalid,
+            reason: "invalid block difficulty".to_string(),
+            data: Some([0xff; 32]),
+        };
+
+        use tokio_util::codec::{FramedRead, FramedWrite};
+        let v_bytes = rt.block_on(async {
+            let mut bytes = Vec::new();
+            {
+                let mut fw = FramedWrite::new(&mut bytes, Codec::builder().finish());
+                fw.send(v.clone())
+                    .await
+                    .expect("message should be serialized");
+            }
+            bytes
+        });
+
+        let v_parsed = rt.block_on(async {
+            let mut fr = FramedRead::new(Cursor::new(&v_bytes), Codec::builder().finish());
+            fr.next()
+                .await
+                .expect("a next message should be available")
+                .expect("that message should deserialize")
+        });
+
+        assert_eq!(v, v_parsed);
+    }
+
     #[test]
     fn filterload_message_too_large_round_trip() {
         zebra_test::init();
```
