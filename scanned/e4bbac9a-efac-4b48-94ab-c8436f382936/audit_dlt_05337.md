# [?] fix(iota-grpc-server): make is_system_transaction total to avoid a request-path panic (#12181)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-07-13
Source: https://github.com/iotaledger/iota/commit/b9d49bfcb8b400e62ced3dec2c958c043e49a539
Type: security-commit

## Details
fix(iota-grpc-server): make is_system_transaction total to avoid a request-path panic (#12181)

# Description of change

`is_system_transaction` in the gRPC transaction filter matched only a
subset of `TransactionKind` variants and fell through to `_ =>
panic!("Unhandled transaction kind")`. The `_` arm catches the `System`
variant, which is a representable value:
`From<&iota_sdk_types::TransactionKind>` maps a concrete system kind
(`AuthenticatorStateUpdateV1`) to the abstract `TransactionKind::System`
marker. A client subscribing/querying with a `System`-kind filter
therefore reaches a `panic!` on the request path if such a transaction
is matched.

This is low priority — the only concrete kind that currently maps to
`System` is the deprecated `AuthenticatorStateUpdateV1`, which is not
produced on live IOTA chains, so the panic is not reachable today. But
it is a latent request-path panic on a representable enum value, so it
is good to have it covered.

The fix makes the match total: `System` classifies as a system
transaction (which is what it represents), and the wildcard arm is
removed so that any future `TransactionKind` variant becomes a compile
error rather than a runtime crash.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [x] Patch-specific tests (correctness, functionality coverage)
- [x] I have added tests that prove my fix is effective or that my
feature works
- [x] I have checked that new and existing unit tests pass locally with
my changes

## Patch
### crates/iota-grpc-server/src/transaction_filter.rs
```diff
@@ -317,12 +317,12 @@ impl TryFrom<proto_filter::TransactionFilter> for TransactionFilter {
 
 fn is_system_transaction(transaction_kind: &TransactionKind) -> bool {
     match transaction_kind {
-        TransactionKind::Genesis
+        TransactionKind::System
+        | TransactionKind::Genesis
         | TransactionKind::ConsensusCommitPrologueV1
         | TransactionKind::EndOfEpoch
         | TransactionKind::RandomnessStateUpdate => true,
         TransactionKind::Programmable => false,
-        _ => panic!("Unhandled transaction kind"),
     }
 }
 
@@ -847,4 +847,21 @@ mod tests {
             command: None,
         }));
     }
+
+    #[test]
+    fn test_is_system_transaction_classifies_every_kind() {
+        // The abstract `System` marker is produced by `From` for concrete
+        // system kinds (e.g. AuthenticatorStateUpdateV1), so it must classify
+        // as a system transaction rather than fall through to a panic.
+        assert!(is_system_transaction(&TransactionKind::System));
+        assert!(is_system_transaction(&TransactionKind::Genesis));
+        assert!(is_system_transaction(
+            &TransactionKind::ConsensusCommitPrologueV1
+        ));
+        assert!(is_system_transaction(&TransactionKind::EndOfEpoch));
+        assert!(is_system_transaction(
+            &TransactionKind::RandomnessStateUpdate
+        ));
+        assert!(!is_system_transaction(&TransactionKind::Programmable));
+    }
 }
```
