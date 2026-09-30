# [?] Adds correct filepath to test_precompile_test_vectors* panics (#1083)

## Summary
Severity: Unknown
Chain: Polkadot
Component: polkadot-evm/frontier
Published: 2023-07-30
Source: https://github.com/polkadot-evm/frontier/commit/e424762b8c2caf2c60b14909aa209014167db616
Type: security-commit

## Details
Adds correct filepath to test_precompile_test_vectors* panics (#1083)

## Patch
### frame/evm/test-vector-support/src/lib.rs
```diff
@@ -119,7 +119,8 @@ impl PrecompileHandle for MockHandle {
 /// The file is expected to be in JSON format and contain an array of test vectors, where each
 /// vector can be deserialized into an "EthConsensusTest".
 pub fn test_precompile_test_vectors<P: Precompile>(filepath: &str) -> Result<(), String> {
-	let data = fs::read_to_string(filepath).expect("Failed to read blake2F.json");
+	let data =
+		fs::read_to_string(filepath).unwrap_or_else(|_| panic!("Failed to read {}", filepath));
 
 	let tests: Vec<EthConsensusTest> = serde_json::from_str(&data).expect("expected json array");
 
@@ -169,7 +170,8 @@ pub fn test_precompile_test_vectors<P: Precompile>(filepath: &str) -> Result<(),
 }
 
 pub fn test_precompile_failure_test_vectors<P: Precompile>(filepath: &str) -> Result<(), String> {
-	let data = fs::read_to_string(filepath).expect("Failed to read json file");
+	let data =
+		fs::read_to_string(filepath).unwrap_or_else(|_| panic!("Failed to read {}", filepath));
 
 	let tests: Vec<EthConsensusFailureTest> =
 		serde_json::from_str(&data).expect("expected json array");
```
