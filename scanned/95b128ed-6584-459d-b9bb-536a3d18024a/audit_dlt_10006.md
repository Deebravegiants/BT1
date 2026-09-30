# [?] avoid panic in service (#2528)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2023-10-19
Source: https://github.com/moonbeam-foundation/moonbeam/commit/15599d0024ab29c113bd1e90ba37281fdf1ce800
Type: security-commit

## Details
avoid panic in service (#2528)

## Patch
### node/service/src/lib.rs
```diff
@@ -1249,18 +1249,17 @@ where
 					_phantom: Default::default(),
 				})),
 				create_inherent_data_providers: move |block: H256, ()| {
-					let current_para_block = client_set_aside_for_cidp
-						.number(block)
-						.expect("Header lookup should succeed")
-						.expect("Header passed in as parent should be present in backend.");
-
+					let maybe_current_para_block = client_set_aside_for_cidp.number(block);
 					let downward_xcm_receiver = downward_xcm_receiver.clone();
 					let hrmp_xcm_receiver = hrmp_xcm_receiver.clone();
 
 					let client_for_xcm = client_set_aside_for_cidp.clone();
 					async move {
 						let time = sp_timestamp::InherentDataProvider::from_system_time();
 
+						let current_para_block = maybe_current_para_block?
+							.ok_or(sp_blockchain::Error::UnknownBlock(block.to_string()))?;
+
 						let mocked_parachain = MockValidationDataInherentDataProvider {
 							current_para_block,
 							relay_offset: 1000,
```
