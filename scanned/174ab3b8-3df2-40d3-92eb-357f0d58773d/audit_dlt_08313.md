# [?] cli: Fix priority fee calculation causing panic on localnet (#3318)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2024-10-18
Source: https://github.com/otter-sec/anchor/commit/b6724d2bcbfb5531224057c49afaa4e8c50c5137
Type: security-commit

## Details
cli: Fix priority fee calculation causing panic on localnet (#3318)

## Patch
### CHANGELOG.md
```diff
@@ -86,6 +86,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 - ts: Update `engines.node` to `>= 17` ([#3301](https://github.com/coral-xyz/anchor/pull/3301)).
 - cli: Use OS-agnostic paths ([#3307](https://github.com/coral-xyz/anchor/pull/3307)).
 - avm: Use `rustc 1.79.0` when installing versions older than v0.31 ([#3315](https://github.com/coral-xyz/anchor/pull/3315)).
+- cli: Fix priority fee calculation causing panic on localnet ([#3318](https://github.com/coral-xyz/anchor/pull/3318)).
 
 ### Breaking
 
```

### cli/src/lib.rs
```diff
@@ -4726,6 +4726,10 @@ fn get_recommended_micro_lamport_fee(client: &RpcClient, priority_fee: Option<u6
     }
 
     let mut fees = client.get_recent_prioritization_fees(&[])?;
+    if fees.is_empty() {
+        // Fees may be empty, e.g. on localnet
+        return Ok(0);
+    }
 
     // Get the median fee from the most recent recent 150 slots' prioritization fee
     fees.sort_unstable_by_key(|fee| fee.prioritization_fee);
```
