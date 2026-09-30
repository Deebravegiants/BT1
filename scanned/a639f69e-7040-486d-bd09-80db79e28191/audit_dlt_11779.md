# [?] fix: Remove `Default` from `ExecutionConfig` to avoid panic in node when network id wasn't provided

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/radixdlt-scrypto
Published: 2024-10-14
Source: https://github.com/radixdlt/radixdlt-scrypto/commit/19c271a21c5a65004bac3ea9c121ab773403a50c
Type: security-commit

## Details
fix: Remove `Default` from `ExecutionConfig` to avoid panic in node when network id wasn't provided

## Patch
### radix-engine/src/transaction/transaction_executor.rs
```diff
@@ -129,13 +129,26 @@ pub struct SystemOverrides {
 }
 
 impl SystemOverrides {
-    pub fn with_network(network_definition: NetworkDefinition) -> Self {
+    const fn internal_default(network_definition: Option<NetworkDefinition>) -> Self {
         Self {
-            network_definition: Some(network_definition),
-            ..Default::default()
+            disable_costing: false,
+            disable_limits: false,
+            disable_auth: false,
+            abort_when_loan_repaid: false,
+            network_definition,
+            costing_parameters: None,
+            limit_parameters: None,
         }
     }
 
+    pub const fn default_with_no_network() -> Self {
+        Self::internal_default(None)
+    }
+
+    pub const fn with_network(network_definition: NetworkDefinition) -> Self {
+        Self::internal_default(Some(network_definition))
+    }
+
     pub fn set_abort_when_loan_repaid(mut self) -> Self {
         self.abort_when_loan_repaid = true;
         self
@@ -144,15 +157,7 @@ impl SystemOverrides {
 
 impl Default for SystemOverrides {
     fn default() -> Self {
-        Self {
-            disable_costing: false,
-            disable_limits: false,
-            disable_auth: false,
-            abort_when_loan_repaid: false,
-            network_definition: None,
-            costing_parameters: None,
-            limit_parameters: None,
-        }
+        Self::default_with_no_network()
     }
 }
 
@@ -167,8 +172,10 @@ pub struct ExecutionConfig {
     pub system_overrides: Option<SystemOverrides>,
 }
 
-impl Default for ExecutionConfig {
-    fn default() -> Self {
+impl ExecutionConfig {
+    /// Creates an `ExecutionConfig` using default configurations.
+    /// This is internal. Clients should use `for_xxx` constructors instead.
+    const fn default_with_no_network() -> Self {
         Self {
             enable_kernel_trace: false,
             enable_cost_breakdown: false,
@@ -177,15 +184,13 @@ impl Default for ExecutionConfig {
             enable_debug_information: false,
         }
     }
-}
 
-impl ExecutionConfig {
     /// Creates an `ExecutionConfig` using default configurations.
     /// This is internal. Clients should use `for_xxx` constructors instead.
-    fn with_network(network_definition: NetworkDefinition) -> Self {
+    fn default_with_network(network_definition: NetworkDefinition) -> Self {
         Self {
             system_overrides: Some(SystemOverrides::with_network(network_definition)),
-            ..Default::default()
+            ..Self::default_with_no_network()
         }
     }
 
@@ -202,7 +207,7 @@ impl ExecutionConfig {
                 network_definition: Some(network_definition),
                 ..Default::default()
             }),
-            ..Default::default()
+            ..Self::default_with_no_network()
         }
     }
 
@@ -214,26 +219,26 @@ impl ExecutionConfig {
                 network_definition: Some(network_definition),
                 ..Default::default()
             }),
-            ..Default::default()
+            ..Self::default_with_no_network()
         }
     }
 
     pub fn for_validator_transaction(network_definition: NetworkDefinition) -> Self {
         Self {
-            ..Self::with_network(network_definition)
+            ..Self::default_with_network(network_definition)
         }
     }
 
     pub fn for_notarized_transaction(network_definition: NetworkDefinition) -> Self {
         Self {
-            ..Self::with_network(network_definition)
+            ..Self::default_with_network(network_definition)
         }
     }
 
     pub fn for_notarized_transaction_rejection_check(
         network_definition: NetworkDefinition,
     ) -> Self {
-        Self::with_network(network_definition)
+        Self::default_with_network(network_definition)
             .update_system_overrides(|overrides| overrides.set_abort_when_loan_repaid())
     }
 
@@ -249,7 +254,7 @@ impl ExecutionConfig {
         Self {
             enable_kernel_trace: true,
             enable_cost_breakdown: true,
-            ..Self::with_network(NetworkDefinition::simulator())
+            ..Self::default_with_network(NetworkDefinition::simulator())
         }
     }
 
@@ -264,7 +269,7 @@ impl ExecutionConfig {
         Self {
             enable_cost_breakdown: true,
             execution_trace: Some(MAX_EXECUTION_TRACE_DEPTH),
-            ..Self::with_network(network_definition)
+            ..Self::default_with_network(network_definition)
         }
     }
 
@@ -277,7 +282,7 @@ impl ExecutionConfig {
                 network_definition: Some(network_definition),
                 ..Default::default()
             }),
-            ..Default::default()
+            ..Self::default_with_no_network()
         }
     }
 
```
