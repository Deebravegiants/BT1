# [?] fix(node-rewards-canister): Fix possible Timer Task Termination via Uncaught Panic (#8152)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-12-21
Source: https://github.com/dfinity/ic/commit/034f7dd28a2ae99d8de6bebe188faa1af8310f8d
Type: security-commit

## Details
fix(node-rewards-canister): Fix possible Timer Task Termination via Uncaught Panic (#8152)

Currently, the HourlySyncTask uses a recursive scheduling pattern: after
executing, it reschedules itself with new_task.schedule_with_delay.
However, if the task panics (e.g., due to .expect() or .unwrap() in
downstream code), the panic rolls back the state and prevents the
rescheduling line from executing. This results in the timer stopping
until a canister upgrade occurs.

**This PR fixes this bug by removing all possible panic occurrences**

## Patch
### rs/node_rewards/canister/src/canister/mod.rs
```diff
@@ -121,7 +121,7 @@ impl NodeRewardsCanister {
         });
         let registry_querier = RegistryQuerier::new(registry_client.clone());
         let version = registry_client.get_latest_version();
-        let subnets_list = registry_querier.subnets_list(version);
+        let subnets_list = registry_querier.subnets_list(version)?;
         let last_day_synced: NaiveDate =
             metrics_manager.update_subnets_metrics(subnets_list).await?;
         canister.with_borrow(|canister| {
```

### rs/node_rewards/canister/src/metrics.rs
```diff
@@ -109,14 +109,9 @@ where
         for (subnet_id, call_result) in subnets_metrics {
             match call_result {
                 Ok(subnet_update) => {
-                    if subnet_update.is_empty() {
-                        ic_cdk::println!("No updates for subnet {}", subnet_id);
-                    } else {
-                        // Update the last timestamp for this subnet.
-                        let last_timestamp = subnet_update
-                            .last()
-                            .map(|metrics| metrics.timestamp_nanos)
-                            .expect("Not empty");
+                    if let Some(last_timestamp) =
+                        subnet_update.last().map(|metrics| metrics.timestamp_nanos)
+                    {
                         self.last_timestamp_per_subnet
                             .borrow_mut()
                             .insert(subnet_id.into(), last_timestamp);
@@ -147,6 +142,8 @@ where
                             subnet_id,
                             date
                         );
+                    } else {
+                        ic_cdk::println!("No updates for subnet {}", subnet_id);
                     }
                 }
                 Err(e) => {
```

### rs/node_rewards/canister/src/registry_querier.rs
```diff
@@ -44,22 +44,27 @@ impl RegistryQuerier {
     }
 
     ///  Returns a list of all subnets present in the registry at the specified version.
-    pub fn subnets_list(&self, version: RegistryVersion) -> Vec<SubnetId> {
+    pub fn subnets_list(&self, version: RegistryVersion) -> Result<Vec<SubnetId>, String> {
         let key = make_subnet_list_record_key();
-        let record = self
+        let record_bytes = self
             .registry_client
             .get_value(key.as_str(), version)
-            .expect("Failed to get SubnetListRecord")
-            .map(|v| {
-                SubnetListRecord::decode(v.as_slice()).expect("Failed to decode SubnetListRecord")
-            })
-            .unwrap_or_default();
+            .map_err(|e| format!("Failed to get SubnetListRecord: {:?}", e))?;
+
+        let record = if let Some(bytes) = record_bytes {
+            SubnetListRecord::decode(bytes.as_slice())
+                .map_err(|e| format!("Failed to decode SubnetListRecord: {:?}", e))?
+        } else {
+            SubnetListRecord::default()
+        };
 
         record
             .subnets
             .into_iter()
             .map(|s| {
-                SubnetId::from(PrincipalId::try_from(s.as_slice()).expect("Invalid subnet ID"))
+                let principal = PrincipalId::try_from(s.as_slice())
+                    .map_err(|e| format!("Invalid subnet ID: {:?}", e))?;
+                Ok(SubnetId::from(principal))
             })
             .collect()
     }
```

### rs/node_rewards/canister/src/registry_querier/tests.rs
```diff
@@ -173,13 +173,13 @@ fn test_subnets_list_returns_expected_subnets() {
         "2025-07-13",
     );
 
-    let got = client.subnets_list(version.into());
+    let got = client.subnets_list(version.into()).unwrap();
 
     let expected: Vec<SubnetId> = vec![subnet_1, subnet_2];
 
     assert_eq!(got, expected);
 
-    let got = client.subnets_list(deleted_version.into());
+    let got = client.subnets_list(deleted_version.into()).unwrap();
 
     let expected: Vec<SubnetId> = vec![];
 
```
