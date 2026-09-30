# [?] fix(prover-autoscaler): fix resource exhaustion detection and aggr mode (#4733)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-03-24
Source: https://github.com/matter-labs/zksync-era/commit/f3d81ced085270a086875ac6187dbee953635831
Type: security-commit

## Details
fix(prover-autoscaler): fix resource exhaustion detection and aggr mode (#4733)

## What ❔

- Replace dead "GCE out of resources" event detection with actual
`FailedScheduling/Insufficient nvidia.com/gpu` events from k8s
scheduler. The old string match was not observed.
- Exclude disabled pools (max_replicas=0) from aggressive mode threshold
calculation — they inflate the denominator and can never have errors,
making the threshold (almost) unreachable in practice.

## Why ❔

Stabilize autoscaling during worst case scenarios

## Is this a breaking change?
- [x] Yes
- [ ] No

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.

## Patch
### prover/crates/bin/prover_autoscaler/src/global/scaler.rs
```diff
@@ -315,20 +315,30 @@ impl<K: Key> Scaler<K> {
                     return false;
                 }
 
-                // Count ALL pools with out_of_resources issues (NeedToMove or scale_errors)
-                let pools_with_errors = pools
+                // Only consider active pools (max_pool_size > 0) for threshold
+                // calculation. Disabled pools can never have errors, so including
+                // them would inflate the denominator and make the threshold harder
+                // to reach.
+                let active_pools: Vec<_> = pools.iter().filter(|p| p.max_pool_size > 0).collect();
+
+                if active_pools.is_empty() {
+                    return false;
+                }
+
+                // Count active pools with out_of_resources issues (NeedToMove or scale_errors).
+                let pools_with_errors = active_pools
                     .iter()
                     .filter(|p| {
                         p.sum_by_pod_status(PodStatus::NeedToMove) > 0 || p.scale_errors > 0
                     })
                     .count();
 
-                let total_pools = pools.len();
+                let total_pools = active_pools.len();
                 let error_percentage = (pools_with_errors * 100) / total_pools;
 
                 if error_percentage >= self.config.aggressive_mode_threshold {
                     tracing::warn!(
-                        "Resource shortage detected: {}/{} pools ({}%) have resource errors (threshold: {}%). Entering AGGRESSIVE MODE.",
+                        "Resource shortage detected: {}/{} active pools ({}%) have resource errors (threshold: {}%). Entering AGGRESSIVE MODE.",
                         pools_with_errors,
                         total_pools,
                         error_percentage,
@@ -338,7 +348,7 @@ impl<K: Key> Scaler<K> {
                     return true;
                 } else if pools_with_errors > 0 {
                     tracing::debug!(
-                        "Resource errors detected: {}/{} pools ({}%) have errors, but threshold {}% not reached",
+                        "Resource errors detected: {}/{} active pools ({}%) have errors, but threshold {}% not reached",
                         pools_with_errors,
                         total_pools,
                         error_percentage,
@@ -2602,4 +2612,123 @@ mod tests {
             "Should request H100s as fallback when L4s exhausted"
         );
     }
+
+    #[tracing_test::traced_test]
+    #[test]
+    fn test_aggressive_mode_excludes_disabled_pools() {
+        // Disabled pools (max_replicas=0) should not count toward the threshold
+        // denominator. Without this fix, disabled pools dilute the error percentage
+        // and make aggressive mode harder to trigger.
+        let scaler_config = Arc::new(ScalerConfig {
+            cluster_priorities: [
+                ("active1".into(), 0),
+                ("active2".into(), 10),
+                ("disabled".into(), 20),
+            ]
+            .into(),
+            apply_min_to_namespace: Some("prover".into()),
+            long_pending_duration: chrono::Duration::seconds(600),
+            scale_errors_duration: chrono::Duration::seconds(3600),
+            aggressive_mode_threshold: 50,
+            aggressive_mode_cooldown: chrono::Duration::seconds(600),
+        });
+
+        let scaler = Scaler::new(
+            QueueReportFields::prover_jobs,
+            "circuit-prover-gpu".into(),
+            0,
+            [
+                ("active1".into(), [(GpuKey(Gpu::L4), 100)].into()),
+                ("active2".into(), [(GpuKey(Gpu::L4), 100)].into()),
+                // Disabled cluster: max_replicas = 0
+                ("disabled".into(), [(GpuKey(Gpu::L4), 0)].into()),
+            ]
+            .into(),
+            [(GpuKey(Gpu::L4), 1500)].into(),
+            0,
+            scaler_config,
+            None,
+        );
+
+        // active1 has an error, active2 is healthy, disabled has no pods.
+        // With the fix: 1/2 active pools = 50% → triggers aggressive mode.
+        // Without the fix: 1/3 total pools = 33% → would NOT trigger.
+        let clusters = Clusters {
+            clusters: [
+                (
+                    "active1".into(),
+                    Cluster {
+                        name: "active1".into(),
+                        namespaces: [(
+                            "prover".into(),
+                            Namespace {
+                                deployments: [("circuit-prover-gpu".into(), Deployment::default())]
+                                    .into(),
+                                pods: [(
+                                    "circuit-prover-gpu-1".into(),
+                                    Pod {
+                                        status: "Pending".into(),
+                                        changed: Utc::now(),
+                                        out_of_resources: true,
+                                        ..Default::default()
+                                    },
+                                )]
+                                .into(),
+                                ..Default::default()
+                            },
+                        )]
+                        .into(),
+                    },
+                ),
+                (
+                    "active2".into(),
+                    Cluster {
+                        name: "active2".into(),
+                        namespaces: [(
+                            "prover".into(),
+                            Namespace {
+                                deployments: [("circuit-prover-gpu".into(), Deployment::default())]
+                                    .into(),
+                                ..Default::default()
+                            },
+                        )]
+                        .into(),
+                    },
+                ),
+                (
+                    "disabled".into(),
+                    Cluster {
+                        name: "disabled".into(),
+                        namespaces: [(
+                            "prover".into(),
+                            Namespace {
+                                deployments: [("circuit-prover-gpu".into(), Deployment::default())]
+                                    .into(),
+                                ..Default::default()
+                            },
+                        )]
+                        .into(),
+                    },
+                ),
+            ]
+            .into(),
+            ..Default::default()
+        };
+
+        let result = scaler.calculate(&"prover".into(), 3000, &clusters);
+
+        // Should have requested pods from active2 (aggressive mode fans out to all pools)
+        let active2_pods = result
+            .get(&PoolKey {
+                cluster: "active2".into(),
+                key: GpuKey(Gpu::L4),
+            })
+            .copied()
+            .unwrap_or(0);
+        assert!(
+            active2_pods > 0,
+            "Aggressive mode should trigger and allocate to active2, got: {:?}",
+            result
+        );
+    }
 }
```

### prover/crates/bin/prover_autoscaler/src/k8s/watcher.rs
```diff
@@ -265,55 +265,51 @@ impl Watcher {
                                     let involved_object_name = e.involved_object.name.clone().unwrap_or_default();
                                     let involved_object_kind = e.involved_object.kind.clone().unwrap_or_default();
 
-                                    if involved_object_kind == "Pod" && event_message.contains("GCE out of resources") {
+                                    let reason = e.reason.clone().unwrap_or_default();
+
+                                    // Detect pods that can't be scheduled due to
+                                    // insufficient GPU resources. The k8s scheduler
+                                    // emits FailedScheduling with "Insufficient
+                                    // nvidia.com/gpu" when no node can fit the pod.
+                                    let is_out_of_resources = involved_object_kind == "Pod"
+                                        && reason == "FailedScheduling"
+                                        && event_message.contains("Insufficient nvidia.com/gpu");
+
+                                    if is_out_of_resources {
                                         tracing::info!(
-                                            "Detected GCE out of resources for pod {} in namespace {}",
+                                            "Detected resource exhaustion for pod {} in namespace {}: {}",
                                             involved_object_name,
-                                            namespace
+                                            namespace,
+                                            event_message
                                         );
                                         let mut cluster_guard = self.cluster.lock().await;
                                         if let Some(ns_data) = cluster_guard.namespaces.get_mut(&namespace.clone()) {
                                             if let Some(pod_data) = ns_data.pods.get_mut(&involved_object_name) {
                                                 pod_data.out_of_resources = true;
-                                                tracing::info!(
-                                                    "Marked pod {} in namespace {} as out of resources",
-                                                    involved_object_name,
-                                                    namespace
-                                                );
                                             } else {
                                                 tracing::warn!(
-                                                    "Pod {} not found in namespace {} for GCE out of resources event",
+                                                    "Pod {} not found in namespace {} for resource exhaustion event",
                                                     involved_object_name,
                                                     namespace
                                                 );
                                             }
                                         } else {
                                             tracing::warn!(
-                                                "Namespace {} not found for GCE out of resources event for pod {}",
+                                                "Namespace {} not found for resource exhaustion event for pod {}",
                                                 namespace,
                                                 involved_object_name
                                             );
                                         }
-                                    }
 
-                                    let reason = e.reason.clone().unwrap_or_default();
-                                    if reason == "FailedScaleUp" && event_message.contains("GCE out of resources") {
+                                        // Also record as a scale error on the namespace.
                                         let name = e.name_any();
                                         let time: DateTime<Utc> = match e.last_timestamp {
                                             Some(t) => t.0,
                                             None => Utc::now(),
                                         };
-                                        tracing::info!(
-                                            "Got FailedScaleUp with GCE out of resources: {}/{}, message: {:?}",
-                                            namespace,
-                                            name,
-                                            event_message
-                                        );
                                         let mut cluster_guard = self.cluster.lock().await;
                                         if let Some(v) = cluster_guard.namespaces.get_mut(&namespace) {
                                             v.scale_errors.push(ScaleEvent { name, time });
-                                        } else {
-                                            tracing::warn!("Namespace not found for FailedScaleUp event: {}", namespace);
                                         }
                                     }
                                 }
```
