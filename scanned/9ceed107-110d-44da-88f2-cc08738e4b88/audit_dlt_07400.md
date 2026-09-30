# [?] fix(script): avoid panics on truncated CREATE2 verification data (#16554)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-08
Source: https://github.com/foundry-rs/foundry/commit/f361ba6944f55cddc9fac36c7159bade777f99fc
Type: security-commit

## Details
fix(script): avoid panics on truncated CREATE2 verification data (#16554)

* fix(script): avoid panics on truncated CREATE2 verification data

Signed-off-by: luangucun <luangucun@outlook.com>

* fix(script): handle short CREATE2 calls

Guard the CREATE2 deployer split and cover short, exact-length, and longer inputs.

Co-authored-by: gomesalexandre <17035424+gomesalexandre@users.noreply.github.com>

* refactor(script): clarify CREATE2 tests

* refactor(script): simplify CREATE2 args slice

* fix(script): warn on malformed create2 data and harden helpers

* fix(script): handle malformed CREATE2 metadata

* test(verify): mock the Blockscout response

Keep verifier argument validation independent of the public Lisk explorer and its TLS availability. Preserve both error snapshots and both successful explicit-verifier cases. AI-assisted CI fix by Centaur.

Co-authored-by: Derek Cofausper <256792747+decofe@users.noreply.github.com>

---------

Signed-off-by: luangucun <luangucun@outlook.com>
Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>
Co-authored-by: gomesalexandre <17035424+gomesalexandre@users.noreply.github.com>
Co-authored-by: DaniPopes <57450786+DaniPopes@users.noreply.github.com>
Co-authored-by: Derek Cofausper <256792747+decofe@users.noreply.github.com>

## Patch
### .changelog/avoid-create2-verify-panic.md
```diff
@@ -0,0 +1,5 @@
+---
+forge-script: patch
+---
+
+Avoid panics in script verification and CREATE2 deployer calls with truncated data.
```

### crates/forge/tests/cli/verify.rs
```diff
@@ -529,10 +529,25 @@ deploy_verify_tests! {
 
 // Tests that verify properly validates verifier arguments.
 // <https://github.com/foundry-rs/foundry/issues/11430>
-forgetest_init!(can_validate_verifier_settings, |prj, cmd| {
+forgetest_async!(can_validate_verifier_settings, |prj, cmd| {
+    foundry_test_utils::util::initialize(prj.root());
     prj.initialize_default_contracts();
     // Build the project to create the cache.
     cmd.forge_fuse().arg("build").assert_success();
+    // Argument validation should not depend on a public block explorer being available.
+    let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
+    let verifier_url = format!("http://{}", listener.local_addr().unwrap());
+    let app = Router::new().fallback(|Query(query): Query<HashMap<String, String>>| async move {
+        assert_eq!(query.get("module").map(String::as_str), Some("contract"));
+        assert_eq!(query.get("action").map(String::as_str), Some("getabi"));
+        assert_eq!(
+            query["address"].parse::<Address>().unwrap(),
+            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2".parse::<Address>().unwrap()
+        );
+        r#"{"status":"1","message":"OK","result":"[]"}"#
+    });
+    let server = tokio::spawn(async move { axum::serve(listener, app).await.unwrap() });
+
     // Use the explicit chain ID so validation does not depend on a public RPC endpoint.
     // No verifier URL.
     cmd.forge_fuse()
@@ -580,7 +595,7 @@ Error: No known Etherscan API URL for chain `4202`. To fix this, please:
             "--verifier",
             "blockscout",
             "--verifier-url",
-            "https://eth.blockscout.com/api",
+            verifier_url.as_str(),
             "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
             "src/Counter.sol:Counter",
         ])
@@ -606,7 +621,7 @@ Contract [src/Counter.sol:Counter] "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
         "--verifier",
         "blockscout",
         "--verifier-url",
-        "https://eth.blockscout.com/api",
+        verifier_url.as_str(),
         "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
         "src/Counter.sol:Counter",
     ])
@@ -619,6 +634,7 @@ Verifying on blockscout...
 Contract [src/Counter.sol:Counter] "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" is already verified. Skipping verification.
 
 "#]]);
+    server.abort();
 });
 
 // Tests that `forge script --broadcast --verify` fails before broadcasting when
```

### crates/script/src/transaction.rs
```diff
@@ -34,20 +34,28 @@ impl<N: Network> ScriptTransactionBuilder<N> {
         create2_deployer: Address,
     ) -> Result<()> {
         if let Some(to) = self.transaction.transaction.to() {
+            self.transaction.call_kind = CallKind::Call;
+            self.transaction.contract_address = Some(to);
+
             if to == create2_deployer {
-                if let Some(input) = self.transaction.transaction.input() {
+                if let Some(input) = self.transaction.transaction.input()
+                    && input.len() >= 32
+                {
                     let (salt, init_code) = input.split_at(32);
 
                     self.set_create(
                         true,
                         create2_deployer.create2_from_code(B256::from_slice(salt), init_code),
                         local_contracts,
                     )?;
+                } else {
+                    let input_len =
+                        self.transaction.transaction.input().map_or(0, |input| input.len());
+                    sh_warn!(
+                        "Skipping CREATE2 decoding for call to deployer {create2_deployer}: input length {input_len} is shorter than the 32-byte salt prefix"
+                    )?;
                 }
             } else {
-                self.transaction.call_kind = CallKind::Call;
-                self.transaction.contract_address = Some(to);
-
                 let Some(data) = self.transaction.transaction.input() else { return Ok(()) };
 
                 if data.len() < SELECTOR_LEN {
@@ -187,8 +195,56 @@ impl<N: Network> From<TransactionWithMetadata<N>> for ScriptTransactionBuilder<N
     }
 }
 
-#[cfg(all(test, feature = "monad"))]
+#[cfg(test)]
 mod tests {
+    use super::*;
+    use alloy_network::Ethereum;
+    use alloy_primitives::{Bytes, address};
+    use alloy_rpc_types::TransactionRequest;
+
+    fn call_to_create2_deployer(input: Option<Bytes>) -> TransactionWithMetadata<Ethereum> {
+        let create2_deployer = address!("0000000000000000000000000000000000001234");
+        let mut transaction = TransactionRequest::default()
+            .with_from(Address::repeat_byte(0x11))
+            .with_to(create2_deployer)
+            .with_nonce(0);
+        if let Some(input) = input {
+            transaction = transaction.with_input(input);
+        }
+        let mut builder = ScriptTransactionBuilder::<Ethereum>::new(
+            TransactionMaybeSigned::new(transaction),
+            "http://localhost:8545".to_string(),
+        );
+        let decoder = CallTraceDecoder::new();
+        builder.set_call(&BTreeMap::new(), decoder, create2_deployer).unwrap();
+        builder.build()
+    }
+
+    #[test]
+    fn short_create2_input_is_classified_as_call() {
+        let create2_deployer = address!("0000000000000000000000000000000000001234");
+        for input in [None, Some(Bytes::new()), Some(Bytes::from(vec![0xab; 31]))] {
+            let transaction = call_to_create2_deployer(input);
+            assert_eq!(transaction.call_kind, CallKind::Call);
+            assert_eq!(transaction.contract_address, Some(create2_deployer));
+        }
+    }
+
+    #[test]
+    fn valid_create2_input_is_classified_as_create2() {
+        let create2_deployer = address!("0000000000000000000000000000000000001234");
+        for input in [Bytes::from(vec![0xab; 32]), Bytes::from(vec![0xab; 33])] {
+            let expected = create2_deployer
+                .create2_from_code(B256::repeat_byte(0xab), input.get(32..).unwrap());
+            let transaction = call_to_create2_deployer(Some(input));
+            assert_eq!(transaction.call_kind, CallKind::Create2);
+            assert_eq!(transaction.contract_address, Some(expected));
+        }
+    }
+}
+
+#[cfg(all(test, feature = "monad"))]
+mod monad_tests {
     use super::*;
     use alloy_network::Ethereum;
     use alloy_primitives::{Bytes, address, keccak256};
```

### crates/script/src/verify.rs
```diff
@@ -186,12 +186,13 @@ impl VerifyBundle {
         libraries: &[String],
         evm_version: EvmVersion,
     ) -> Option<VerifyArgs> {
+        let init_code = data.get(create2_offset..)?;
         for (artifact, contract) in self.known_contracts.iter() {
             let Some(bytecode) = contract.bytecode() else { continue };
             // If it's a CREATE2, the tx.data comes with a 32-byte salt in the beginning
             // of the transaction
-            if data.split_at(create2_offset).1.starts_with(bytecode) {
-                let constructor_args = data.split_at(create2_offset + bytecode.len()).1.to_vec();
+            if init_code.starts_with(bytecode) {
+                let constructor_args = init_code[bytecode.len()..].to_vec();
 
                 if artifact.source.extension().is_some_and(|e| e.to_str() == Some("vy")) {
                     warn!("Skipping verification of Vyper contract: {}", artifact.name);
@@ -456,8 +457,18 @@ async fn verify_contracts<FEN: FoundryEvmNetwork>(
                 continue;
             };
             let receipt = &mut sequence.receipts[receipt_index];
+            let malformed_create2 =
+                tx.is_create2() && tx.tx().input().is_none_or(|data| data.len() < 32);
+            if malformed_create2 {
+                let input_len = tx.tx().input().map_or(0, |data| data.len());
+                let _ = sh_warn!(
+                    "Skipping verification for CREATE2 transaction {tx_hash}: input length {input_len} is shorter than the 32-byte salt prefix."
+                );
+            }
+
             // create2 hash offset
-            let offset = if tx.is_create2()
+            let offset = if !malformed_create2
+                && tx.is_create2()
                 && let Some(contract_address) = tx.contract_address
             {
                 receipt.set_contract_address(contract_address);
@@ -467,7 +478,9 @@ async fn verify_contracts<FEN: FoundryEvmNetwork>(
             };
 
             // Verify contract created directly from the transaction
-            if let (Some(address), Some(data)) = (receipt.contract_address(), tx.tx().input()) {
+            if !malformed_create2
+                && let (Some(address), Some(data)) = (receipt.contract_address(), tx.tx().input())
+            {
                 match verify.get_verify_args(
                     address,
                     offset,
@@ -635,7 +648,13 @@ mod tests {
         sourcify_api_url, take_matching_index,
     };
     use alloy_chains::Chain;
+    use alloy_primitives::{Address, Bytes};
+    use foundry_compilers::{
+        ArtifactId,
+        artifacts::{BytecodeObject, CompactBytecode, CompactContractBytecode, EvmVersion},
+    };
     use foundry_config::Config;
+    use semver::Version;
 
     fn bundle(config: &Config, verifier: VerifierArgs) -> VerifyBundle {
         let project = config.project().unwrap();
@@ -649,6 +668,70 @@ mod tests {
         )
     }
 
+    fn bundle_with_bytecode(bytecode: Bytes) -> VerifyBundle {
+        let config = Config::default();
+        let mut verify = bundle(&config, VerifierArgs::default());
+        verify.known_contracts = ContractsByArtifact::new([(
+            ArtifactId {
+                path: "out/Test.json".into(),
+                name: "Test".into(),
+                source: "src/Test.sol".into(),
+                version: Version::new(0, 8, 30),
+                build_id: String::new(),
+                profile: "default".into(),
+            },
+            CompactContractBytecode {
+                abi: Some(Default::default()),
+                bytecode: Some(CompactBytecode {
+                    object: BytecodeObject::Bytecode(bytecode),
+                    source_map: None,
+                    link_references: Default::default(),
+                }),
+                deployed_bytecode: None,
+            },
+        )]);
+        verify
+    }
+
+    #[test]
+    fn truncated_create2_data_is_unverifiable() {
+        let bytecode = Bytes::from_static(&[0x60, 0x00]);
+        let verify = bundle_with_bytecode(bytecode);
+        let address = Address::ZERO;
+
+        for data in [Bytes::new(), Bytes::from(vec![0; 31])] {
+            assert!(
+                verify.get_verify_args(address, 32, &data, &[], EvmVersion::London).is_none(),
+                "truncated data should not produce verification args"
+            );
+        }
+    }
+
+    #[test]
+    fn salt_only_create2_data_is_unverifiable() {
+        let verify = bundle_with_bytecode(Bytes::from_static(&[0x60, 0x00]));
+        let address = Address::ZERO;
+        let salt_only = Bytes::from(vec![0; 32]);
+        assert!(
+            verify.get_verify_args(address, 32, &salt_only, &[], EvmVersion::London).is_none(),
+            "valid salt-only data should not match non-empty bytecode"
+        );
+    }
+
+    #[test]
+    fn valid_create2_data_produces_verification_args() {
+        let bytecode = Bytes::from_static(&[0x60, 0x00]);
+        let verify = bundle_with_bytecode(bytecode.clone());
+        let address = Address::ZERO;
+        let mut data = vec![0; 32];
+        data.extend_from_slice(&bytecode);
+        data.extend_from_slice(&[0xaa, 0xbb]);
+        let args = verify
+            .get_verify_args(address, 32, &data, &[], EvmVersion::London)
+            .expect("valid CREATE2 data should produce verification args");
+        assert_eq!(args.constructor_args.as_deref(), Some("aabb"));
+    }
+
     #[test]
     fn receipt_matching_is_hash_based_and_consumes_duplicate_hashes_in_order() {
         let reversed = [(2, "second"), (1, "first")];
```
