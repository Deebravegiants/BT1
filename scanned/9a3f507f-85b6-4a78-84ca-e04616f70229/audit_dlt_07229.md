# [?] [MFP] fix panic when calculating max scores (#23685)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-09-22
Source: https://github.com/MystenLabs/sui/commit/8ba1badef2fc7da58136f8a1dc295ee456066a27
Type: security-commit

## Details
[MFP] fix panic when calculating max scores (#23685)

## Description 

Fixing the panic caused via the access of validator stats during
calculating the max scores when committee changes. Simtest failure here:
https://github.com/MystenLabs/sui/actions/runs/17877922438/job/50841890707

## Test plan 

CI/PT

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

## Patch
### crates/sui-core/src/validator_client_monitor/monitor.rs
```diff
@@ -155,7 +155,7 @@ where
                 }
             }
 
-            self.update_cached_scores();
+            self.update_cached_scores(&authority_agg);
         }
     }
 }
@@ -165,8 +165,7 @@ impl<A: Clone> ValidatorClientMonitor<A> {
     ///
     /// This method is called periodically after health checks complete to update
     /// the cached validator scores.
-    fn update_cached_scores(&self) {
-        let authority_agg = self.authority_aggregator.load();
+    fn update_cached_scores(&self, authority_agg: &AuthorityAggregator<A>) {
         let committee = &authority_agg.committee;
         let mut cached_scores = self.cached_scores.write();
 
@@ -279,8 +278,8 @@ impl<A: Clone> ValidatorClientMonitor<A> {
     }
 
     #[cfg(test)]
-    pub fn force_update_cached_scores(&self) {
-        self.update_cached_scores();
+    pub fn force_update_cached_scores(&self, authority_agg: &AuthorityAggregator<A>) {
+        self.update_cached_scores(authority_agg);
     }
 
     #[cfg(test)]
```

### crates/sui-core/src/validator_client_monitor/stats.rs
```diff
@@ -167,7 +167,11 @@ impl ClientObservedStats {
         let mut max_latencies = HashMap::new();
 
         for validator in committee.names() {
-            let stats = self.validator_stats.get(validator).unwrap();
+            // It's possible that a reconfiguration happened and the validator is no longer in the committee.
+            let Some(stats) = self.validator_stats.get(validator) else {
+                continue;
+            };
+
             // We are specifically excluding from the max latencies calculations the validators that are meant to be excluded
             // from the score calculations anyways. Only the ones participating in the pool should be considered to avoid score inflation.
             let is_excluded = if let Some(exclusion_time) = stats.exclusion_time {
```

### crates/sui-core/src/validator_client_monitor/tests.rs
```diff
@@ -551,7 +551,7 @@ mod client_monitor_tests {
         }
 
         // Force update cached scores (in production this happens in the health check loop)
-        monitor.force_update_cached_scores();
+        monitor.force_update_cached_scores(&auth_agg);
 
         // Select validators with k=2
         let selected =
@@ -599,7 +599,7 @@ mod client_monitor_tests {
         }
 
         // Force update cached scores (in production this happens in the health check loop)
-        monitor.force_update_cached_scores();
+        monitor.force_update_cached_scores(&auth_agg);
 
         // Select validators with k=3
         let selected =
@@ -657,7 +657,7 @@ mod client_monitor_tests {
         }
 
         // Force update cached scores (in production this happens in the health check loop)
-        monitor.force_update_cached_scores();
+        monitor.force_update_cached_scores(&auth_agg);
 
         // Should still select validators from the provided committee
         let selected =
@@ -693,7 +693,7 @@ mod client_monitor_tests {
         }
 
         // Force update cached scores (in production this happens in the health check loop)
-        monitor.force_update_cached_scores();
+        monitor.force_update_cached_scores(&auth_agg);
 
         // Request more validators than available
         let selected =
@@ -733,7 +733,7 @@ mod client_monitor_tests {
         }
 
         // Force update cached scores (in production this happens in the health check loop)
-        monitor.force_update_cached_scores();
+        monitor.force_update_cached_scores(&auth_agg);
 
         // Select validators with k=2 for the shared object tx type
         let selected =
@@ -828,6 +828,9 @@ mod client_monitor_tests {
         assert!(monitor.has_validator_stats(&initial_validators[0]));
         assert!(monitor.has_validator_stats(&initial_validators[1]));
         assert!(!monitor.has_validator_stats(&initial_validators[2]));
+
+        // Calculate the scores for the validators and ensure this is successful
+        monitor.force_update_cached_scores(&initial_auth_agg);
     }
 
     #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
```
