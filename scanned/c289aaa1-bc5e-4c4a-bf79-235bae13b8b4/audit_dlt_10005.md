# [?] fix: propagate error instead of panicking in manual sealing (#2983)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2024-09-28
Source: https://github.com/moonbeam-foundation/moonbeam/commit/a8fece37fa913e0bbe848006d69f9c125d12ab0a
Type: security-commit

## Details
fix: propagate error instead of panicking in manual sealing (#2983)

## Patch
### node/service/src/lib.rs
```diff
@@ -1808,23 +1808,28 @@ where
 			.client
 			.header(hash)
 			.map_err(|e| sp_inherents::Error::Application(Box::new(e)))?
-			.expect("Best block header should be present")
+			.ok_or(sp_inherents::Error::Application(
+				"Best block header should be present".into(),
+			))?
 			.digest;
 		// Get the nimbus id from the digest.
 		let nimbus_id = digest
 			.logs
 			.iter()
 			.find_map(|x| {
 				if let DigestItem::PreRuntime(nimbus_primitives::NIMBUS_ENGINE_ID, nimbus_id) = x {
-					Some(
-						NimbusId::from_slice(nimbus_id.as_slice())
-							.expect("Nimbus pre-runtime digest should be valid"),
-					)
+					Some(NimbusId::from_slice(nimbus_id.as_slice()).map_err(|_| {
+						sp_inherents::Error::Application(
+							"Nimbus pre-runtime digest should be valid".into(),
+						)
+					}))
 				} else {
 					None
 				}
 			})
-			.expect("Nimbus pre-runtime digest should be present");
+			.ok_or(sp_inherents::Error::Application(
+				"Nimbus pre-runtime digest should be present".into(),
+			))??;
 		// Remove the old VRF digest.
 		let pos = digest.logs.iter().position(|x| {
 			matches!(
```
