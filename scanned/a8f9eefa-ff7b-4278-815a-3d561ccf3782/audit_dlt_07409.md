# [?] fix(common): don't panic when Etherscan reports a proxy with no implementation (#16545)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-02
Source: https://github.com/foundry-rs/foundry/commit/d63a096e628baaed6a9dd6889fac2983617f9939
Type: security-commit

## Details
fix(common): don't panic when Etherscan reports a proxy with no implementation (#16545)

* fix(common): don't panic when Etherscan reports a proxy with no resolved implementation

find_source's proxy-following path called metadata.implementation.unwrap()
whenever metadata.proxy != 0, but Etherscan (and compatible explorers) can
report Proxy: 1 while Implementation comes back empty - which
foundry_block_explorers' own deserialize_address_opt turns into None (see
that crate's own can_deserialize_address_opt test, which cites a real
address exhibiting this exact shape).

Extract the proxy/implementation decision into resolve_proxy_implementation
so it's directly unit-testable without a network client, and fall back to
the metadata's own source instead of panicking when a proxy has no
resolved implementation - mirroring the existing ContractCodeNotVerified
fallback a few lines below.

Regression test constructs the real Metadata type from a realistic
Etherscan payload shape and confirms resolve_proxy_implementation returns
None instead of panicking; confirmed to panic against the original
.unwrap()-based logic.

* chore: add changelog entry for #16545

* refactor(common): inline proxy-implementation decision into find_source

Per review feedback, inline the resolve_proxy_implementation helper
directly into find_source rather than keeping it as a separate function.
The regression tests now exercise the same one-line decision inline
instead of calling a named helper.

* style: trim verbose comments per review

mablr: 'please make the comments more concise, agents are too verbose'

## Patch
### .changelog/pr-16545.md
```diff
@@ -0,0 +1,5 @@
+---
+foundry-common: patch
+---
+
+Fixed `find_source` panicking (`unwrap()` on a missing `Implementation` address) when Etherscan reports a contract as a proxy but returns an empty implementation field.
```

### crates/common/src/abi.rs
```diff
@@ -175,10 +175,10 @@ pub fn find_source(
         trace!(%address, "find Etherscan source");
         let source = client.contract_source_code(address).await?;
         let metadata = source.items.first().wrap_err("Etherscan returned no data")?;
-        if metadata.proxy == 0 {
-            Ok(source)
-        } else {
-            let implementation = metadata.implementation.unwrap();
+        // `Proxy: 1` can still come with an empty `Implementation` (unresolved/unverified);
+        // treat that like "not a proxy" instead of panicking on `.unwrap()`.
+        let implementation = if metadata.proxy == 0 { None } else { metadata.implementation };
+        if let Some(implementation) = implementation {
             sh_println!(
                 "Contract at {address} is a proxy, trying to fetch source at {implementation}..."
             )?;
@@ -194,6 +194,11 @@ pub fn find_source(
                     }
                 }
             }
+        } else {
+            if metadata.proxy != 0 {
+                error!(%address, "Etherscan reports this contract as a proxy but returned no implementation address");
+            }
+            Ok(source)
         }
     })
 }
@@ -210,6 +215,69 @@ mod tests {
     use alloy_dyn_abi::EventExt;
     use alloy_primitives::{B256, U256};
 
+    /// `Proxy: 1` with an empty `Implementation` used to panic on `.unwrap()`
+    /// (real-world shape, see `foundry_block_explorers`' own `can_deserialize_address_opt` test).
+    #[test]
+    fn test_proxy_without_implementation_does_not_panic() {
+        use foundry_block_explorers::contract::Metadata;
+
+        let json = serde_json::json!({
+            "SourceCode": "// dummy",
+            "ABI": "[]",
+            "ContractName": "Dummy",
+            "CompilerVersion": "v0.8.0+commit.c7dfd78e",
+            "OptimizationUsed": "0",
+            "Runs": "200",
+            "ConstructorArguments": "",
+            "EVMVersion": "Default",
+            "Library": "",
+            "LicenseType": "None",
+            "Proxy": "1",
+            "Implementation": "",
+            "SwarmSource": ""
+        });
+
+        let metadata: Metadata =
+            serde_json::from_value(json).expect("realistic Etherscan payload must deserialize");
+
+        // This is exactly the combination that used to reach `.unwrap()` on `None`.
+        assert_eq!(metadata.proxy, 1, "Proxy: 1 must deserialize to a nonzero proxy flag");
+        assert_eq!(
+            metadata.implementation, None,
+            "an empty Implementation string must deserialize to None, not a parsed address"
+        );
+
+        // Must not panic: this is the exact decision `find_source` makes.
+        let implementation = if metadata.proxy == 0 { None } else { metadata.implementation };
+        assert_eq!(implementation, None);
+    }
+
+    #[test]
+    fn proxy_implementation_decision_follows_real_implementation() {
+        use alloy_primitives::address;
+        use foundry_block_explorers::contract::Metadata;
+
+        let json = serde_json::json!({
+            "SourceCode": "// dummy",
+            "ABI": "[]",
+            "ContractName": "Dummy",
+            "CompilerVersion": "v0.8.0+commit.c7dfd78e",
+            "OptimizationUsed": "0",
+            "Runs": "200",
+            "ConstructorArguments": "",
+            "EVMVersion": "Default",
+            "Library": "",
+            "LicenseType": "None",
+            "Proxy": "1",
+            "Implementation": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
+            "SwarmSource": ""
+        });
+        let metadata: Metadata = serde_json::from_value(json).unwrap();
+
+        let implementation = if metadata.proxy == 0 { None } else { metadata.implementation };
+        assert_eq!(implementation, Some(address!("0x1F98431c8aD98523631AE4a59f267346ea31F984")));
+    }
+
     #[test]
     fn test_get_func() {
         let func = get_func("function foo(uint256 a, uint256 b) returns (uint256)");
```
