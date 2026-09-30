# [?] primitives: fix TransactionDecoder::end to not panic on early calls to end

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-10-13
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/93db1e0d306fd0faa887b3029efcb64aee581d5b
Type: security-commit

## Details
primitives: fix TransactionDecoder::end to not panic on early calls to end

If the data stream ends early we shouldn't panic. This is not a programmer
error. It indicates that we ran out of data.

This one has observable changes. Unit test in next commit.

## Patch
### primitives/src/transaction.rs
```diff
@@ -514,15 +514,18 @@ impl Decoder for TransactionDecoder {
 
     #[inline]
     fn end(self) -> Result<Self::Output, Self::Error> {
-        use TransactionDecoderState as State;
+        use {
+            TransactionDecoderError as E, TransactionDecoderErrorInner as Inner,
+            TransactionDecoderState as State,
+        };
 
         match self.state {
-            State::Version(_) => panic!("tried to end decoder in state: Version"),
-            State::Inputs(..) => panic!("tried to end decoder in state: Inputs"),
-            State::SegwitFlag(..) => panic!("tried to end decoder in state: SegwitFlag"),
-            State::Outputs(..) => panic!("tried to end decoder in state: Outputs"),
-            State::Witnesses(..) => panic!("tried to end decoder in state: Witnesses"),
-            State::LockTime(..) => panic!("tried to end decoder in state: LockTime"),
+            State::Version(_) => Err(E(Inner::EarlyEnd("version"))),
+            State::Inputs(..) => Err(E(Inner::EarlyEnd("inputs"))),
+            State::SegwitFlag(..) => Err(E(Inner::EarlyEnd("segwit flag"))),
+            State::Outputs(..) => Err(E(Inner::EarlyEnd("outputs"))),
+            State::Witnesses(..) => Err(E(Inner::EarlyEnd("witnesses"))),
+            State::LockTime(..) => Err(E(Inner::EarlyEnd("locktime"))),
             State::Done(tx) => Ok(tx),
             State::Errored => panic!("call to end() after decoder errored"),
         }
@@ -622,6 +625,9 @@ enum TransactionDecoderErrorInner {
     NoWitnesses,
     /// Error while decoding the `lock_time`.
     LockTime(LockTimeDecoderError),
+    /// Attempt to call `end()` before the transaction was complete. Holds
+    /// a description of the current state.
+    EarlyEnd(&'static str),
 }
 
 #[cfg(feature = "alloc")]
@@ -672,6 +678,7 @@ impl fmt::Display for TransactionDecoderError {
             E::Witness(ref e) => write_err!(f, "transaction decoder error"; e),
             E::NoWitnesses => write!(f, "non-empty Segwit transaction with no witnesses"),
             E::LockTime(ref e) => write_err!(f, "transaction decoder error"; e),
+            E::EarlyEnd(s) => write!(f, "early end of transaction (still decoding {})", s),
         }
     }
 }
@@ -690,6 +697,7 @@ impl std::error::Error for TransactionDecoderError {
             E::Witness(ref e) => Some(e),
             E::NoWitnesses => None,
             E::LockTime(ref e) => Some(e),
+            E::EarlyEnd(_) => None,
         }
     }
 }
```
