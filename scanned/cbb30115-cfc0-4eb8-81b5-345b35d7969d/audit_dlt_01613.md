# [?] [TrafficControl] Enable DOS protection by default (dryRun)  (#22143)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-05-21
Source: https://github.com/MystenLabs/sui/commit/9006185009afa2fe239fec771a7d067437814a42
Type: security-commit

## Details
[TrafficControl] Enable DOS protection by default (dryRun)  (#22143)

## Description 

In order for the traffic controller to be enabled in any form,
validators must add a `policy-config:` block to their nodes, copying the
examples from:
https://gist.github.com/williampsmith/4de166d8be9bb9e183594d631452fb19

I can't see good reason not to turn traffic controller on in dry-run
mode by default, since it's essentially what we're asking operators to
do in the above guide. The configs I used in
`default_dos_protection_policy()` are just cut and paste from that gist
(I'm not certain those are the best defaults, but seems that Will
thought so)

## Test plan 

I've tested these changes locally.

we currently have 37 mainnet validators with some type of `PolicyConfig`
enabled
<img width="598" alt="image"
src="https://github.com/user-attachments/assets/6a2b9d78-1bf0-40d5-8666-5f762bd39ee4"
/>

and 56 testnet validators:
<img width="450" alt="image"
src="https://github.com/user-attachments/assets/141981c5-c361-4c32-bd3a-3717ee90f147"
/>


---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [x] Nodes (Validators and Full nodes): DoS protection is enabled in
dryRun mode by default for validators
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

### crates/sui-config/src/node.rs
```diff
@@ -172,7 +172,10 @@ pub struct NodeConfig {
     pub run_with_range: Option<RunWithRange>,
 
     // For killswitch use None
-    #[serde(skip_serializing_if = "Option::is_none")]
+    #[serde(
+        skip_serializing_if = "Option::is_none",
+        default = "default_traffic_controller_policy_config"
+    )]
     pub policy_config: Option<PolicyConfig>,
 
     #[serde(skip_serializing_if = "Option::is_none")]
@@ -1244,6 +1247,10 @@ fn default_authority_overload_config() -> AuthorityOverloadConfig {
     AuthorityOverloadConfig::default()
 }
 
+fn default_traffic_controller_policy_config() -> Option<PolicyConfig> {
+    Some(PolicyConfig::default_dos_protection_policy())
+}
+
 #[derive(Debug, Clone, PartialEq, Deserialize, Serialize, Eq)]
 pub struct Genesis {
     #[serde(flatten)]
```

### crates/sui-core/src/authority_server.rs
```diff
@@ -9,8 +9,9 @@ use futures::TryFutureExt;
 use mysten_metrics::spawn_monitored_task;
 use mysten_network::server::SUI_TLS_SERVER_NAME;
 use prometheus::{
-    register_histogram_with_registry, register_int_counter_vec_with_registry,
-    register_int_counter_with_registry, Histogram, IntCounter, IntCounterVec, Registry,
+    register_gauge_with_registry, register_histogram_with_registry,
+    register_int_counter_vec_with_registry, register_int_counter_with_registry, Gauge, Histogram,
+    IntCounter, IntCounterVec, Registry,
 };
 use std::{
     io,
@@ -211,6 +212,7 @@ pub struct ValidatorServiceMetrics {
     forwarded_header_invalid: IntCounter,
     forwarded_header_not_included: IntCounter,
     client_id_source_config_mismatch: IntCounter,
+    x_forwarded_for_num_hops: Gauge,
 }
 
 impl ValidatorServiceMetrics {
@@ -369,6 +371,12 @@ impl ValidatorServiceMetrics {
                 registry,
             )
             .unwrap(),
+            x_forwarded_for_num_hops: register_gauge_with_registry!(
+                "validator_service_x_forwarded_for_num_hops",
+                "Number of hops in x-forwarded-for header",
+                registry,
+            )
+            .unwrap(),
         }
     }
 
@@ -1426,6 +1434,17 @@ impl ValidatorService {
         request: &tonic::Request<T>,
         source: &ClientIdSource,
     ) -> Option<IpAddr> {
+        let forwarded_header = request.metadata().get_all("x-forwarded-for").iter().next();
+
+        if let Some(header) = forwarded_header {
+            let num_hops = header
+                .to_str()
+                .map(|h| h.split(',').count().saturating_sub(1))
+                .unwrap_or(0);
+
+            self.metrics.x_forwarded_for_num_hops.set(num_hops as f64);
+        }
+
         match source {
             ClientIdSource::SocketAddr => {
                 let socket_addr: Option<SocketAddr> = request.remote_addr();
```

### crates/sui-types/src/traffic_control.rs
```diff
@@ -1,7 +1,7 @@
 // Copyright (c) Mysten Labs, Inc.
 // SPDX-License-Identifier: Apache-2.0
 
-use serde::{Deserialize, Serialize};
+use serde::{de::Deserializer, Deserialize, Serialize};
 use serde_with::serde_as;
 use std::path::PathBuf;
 
@@ -102,6 +102,15 @@ impl Weight {
     }
 }
 
+fn validate_sample_rate<'de, D>(deserializer: D) -> Result<Weight, D::Error>
+where
+    D: Deserializer<'de>,
+{
+    let value = f32::deserialize(deserializer)?;
+    Weight::new(value)
+        .map_err(|_| serde::de::Error::custom("spam-sample-rate must be between 0.0 and 1.0"))
+}
+
 impl PartialEq for Weight {
     fn eq(&self, other: &Self) -> bool {
         self.value() == other.value()
@@ -213,6 +222,7 @@ pub enum PolicyType {
     /// Blocks connection_ip after reaching a tally frequency (tallies per second)
     /// of `threshold`, as calculated over an average window of `window_size_secs`
     /// with granularity of `update_interval_secs`
+    #[serde(rename = "freq-threshold", alias = "FreqThreshold")]
     FreqThreshold(FreqThresholdConfig),
 
     /* Below this point are test policies, and thus should not be used in production */
@@ -242,7 +252,10 @@ pub struct PolicyConfig {
     pub error_policy_type: PolicyType,
     #[serde(default = "default_channel_capacity")]
     pub channel_capacity: usize,
-    #[serde(default = "default_spam_sample_rate")]
+    #[serde(
+        default = "default_spam_sample_rate",
+        deserialize_with = "validate_sample_rate"
+    )]
     /// Note that this sample policy is applied on top of the
     /// endpoint-specific sample policy (not configurable) which
     /// weighs endpoints by the relative effort required to serve
@@ -274,6 +287,30 @@ impl Default for PolicyConfig {
     }
 }
 
+impl PolicyConfig {
+    pub fn default_dos_protection_policy() -> PolicyConfig {
+        PolicyConfig {
+            client_id_source: ClientIdSource::SocketAddr,
+            spam_policy_type: PolicyType::FreqThreshold(FreqThresholdConfig {
+                client_threshold: 500,
+                window_size_secs: 5,
+                update_interval_secs: 1,
+                ..FreqThresholdConfig::default()
+            }),
+            error_policy_type: PolicyType::FreqThreshold(FreqThresholdConfig {
+                client_threshold: 50,
+                window_size_secs: 5,
+                update_interval_secs: 1,
+                ..FreqThresholdConfig::default()
+            }),
+            channel_capacity: 6000,
+            spam_sample_rate: Weight::new(1.0).unwrap(),
+            dry_run: true,
+            ..PolicyConfig::default()
+        }
+    }
+}
+
 pub fn default_client_id_source() -> ClientIdSource {
     ClientIdSource::SocketAddr
 }
```
