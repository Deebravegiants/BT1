# [?] fix(core): reject amount addition overflow (#8686)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-06-12
Source: https://github.com/fedimint/fedimint/commit/25ef880c3af703d14b4a18f316053825306f8173
Type: security-commit

## Details
fix(core): reject amount addition overflow (#8686)

Summary

Reject overflows when combining multi-unit amount maps.

Details

`Amounts::checked_add` delegated to `checked_add_mut` but ignored a
`None` result, so callers could observe `Some` even when adding an
amount overflowed. Propagate the overflow result so funding checks and
other callers fail closed.

This also adds a regression test covering an output plus fee overflow in
the funding verifier.

Testing

- `cargo test -p fedimint-server
consensus::transaction::tests::funding_verifier_rejects_output_plus_fee_overflow`
- `just final-lint`

## Patch
### fedimint-core/src/module/mod.rs
```diff
@@ -144,7 +144,7 @@ impl Amounts {
     }
 
     pub fn checked_add(mut self, rhs: &Self) -> Option<Self> {
-        self.checked_add_mut(rhs);
+        self.checked_add_mut(rhs)?;
 
         Some(self)
     }
```

### fedimint-server/src/consensus/transaction/tests.rs
```diff
@@ -85,3 +85,21 @@ fn sanity_test_funding_verifier_2() {
     assert!(v.clone().verify_funding(VERIFIER_OLD).is_err());
     assert!(v.clone().verify_funding(VERIFIER_NEW).is_ok());
 }
+
+#[test]
+fn funding_verifier_rejects_output_plus_fee_overflow() {
+    let mut v = super::FundingVerifier::default();
+
+    v.add_input(TransactionItemAmounts {
+        amounts: Amounts::new_bitcoin(Amount::from_msats(u64::MAX)),
+        fees: Amounts::ZERO,
+    })
+    .unwrap()
+    .add_output(TransactionItemAmounts {
+        amounts: Amounts::new_bitcoin(Amount::from_msats(u64::MAX)),
+        fees: Amounts::new_bitcoin_msats(1),
+    })
+    .unwrap();
+
+    assert!(v.verify_funding(VERIFIER_NEW).is_err());
+}
```
