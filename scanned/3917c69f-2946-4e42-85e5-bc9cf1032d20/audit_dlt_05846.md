# [?] fix(governance): don't panic when a node provider has no id (#11092)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-08-13
Source: https://github.com/dfinity/ic/commit/8be8631fa4cce7784d6da714cbeea6711a0f5e45
Type: security-commit

## Details
fix(governance): don't panic when a node provider has no id (#11092)

`validate_assign_noid_payload` was calling `.unwrap()` on `np.id`, which
is an `Option`. If any node provider in governance state has `id =
None`, this panics and blocks all `AddNodeOperator` proposal
submissions.

Fixed by comparing the `Option` values directly instead of unwrapping
them.

## Patch
### rs/nns/governance/src/governance.rs
```diff
@@ -5018,13 +5018,22 @@ impl Governance {
             }
         };
 
-        if decoded_payload.node_provider_principal_id.is_none() {
+        let Some(node_provider_id_of_node_operator) = decoded_payload.node_provider_principal_id
+        else {
             return Err("The payload's node_provider_principal_id field was None".to_string());
-        }
+        };
 
-        let is_registered = node_providers
-            .iter()
-            .any(|np| np.id.unwrap() == decoded_payload.node_provider_principal_id.unwrap());
+        let is_registered = node_providers.iter().any(|np| {
+            let Some(np_id) = np.id else {
+                println!(
+                    "{}Skipping node provider with no id while checking registration.",
+                    LOG_PREFIX,
+                );
+                return false;
+            };
+
+            np_id == node_provider_id_of_node_operator
+        });
         if !is_registered {
             return Err("The node provider specified in the payload is not registered".to_string());
         }
```

### rs/nns/governance/src/governance/tests/mod.rs
```diff
@@ -1399,6 +1399,66 @@ fn test_validate_execute_nns_function() {
     }
 }
 
+/// A node provider stored with id = None (possible from pre-validation-era state) must not
+/// cause validate_assign_noid_payload to panic. It should be treated as non-matching and
+/// the function should return a clean "not registered" error.
+#[test]
+fn test_validate_assign_noid_tolerates_node_provider_with_none_id() {
+    // Step 1: Prepare the world.
+    // Mix a legacy entry (id = None) with a valid entry to ensure neither panics nor false match.
+    let governance = Governance::new(
+        api::Governance {
+            economics: Some(api::NetworkEconomics::with_default_values()),
+            node_providers: vec![
+                api::NodeProvider {
+                    // This used to cause a panic in the code under test,
+                    // whereas, now, it just logs a warning.
+                    id: None,
+                    ..Default::default()
+                },
+                api::NodeProvider {
+                    id: Some(PrincipalId::new_node_test_id(1)),
+                    ..Default::default()
+                },
+            ],
+            ..Default::default()
+        },
+        Arc::new(MockEnvironment::new(vec![], 100)),
+        Arc::new(StubIcpLedger {}),
+        Arc::new(StubCMC {}),
+        Box::new(MockRandomness::new()),
+    );
+
+    let new_valid_assign_node_operator_proposal_action = |node_provider_principal_id| {
+        let payload = Encode!(&AddNodeOperatorPayload {
+            node_provider_principal_id: Some(node_provider_principal_id),
+            ..Default::default()
+        })
+        .unwrap();
+        ValidExecuteNnsFunction::try_from(ExecuteNnsFunction {
+            nns_function: NnsFunction::AssignNoid as i32,
+            payload,
+        })
+        .unwrap()
+    };
+
+    // Step 2: Run the code under test.
+    // The following calls must not panic — that's the main thing this test verifies.
+    let unregistered_node_provider_result = governance.validate_execute_nns_function(
+        &new_valid_assign_node_operator_proposal_action(PrincipalId::new_node_test_id(99)),
+    );
+    let registered_node_provider_result = governance.validate_execute_nns_function(
+        &new_valid_assign_node_operator_proposal_action(PrincipalId::new_node_test_id(1)),
+    );
+
+    // Step 3: Verify result(s).
+    // Unregistered provider → clean error, no panic.
+    let err = unregistered_node_provider_result.unwrap_err();
+    assert!(err.error_message.contains("not registered"));
+    // Registered provider → ok.
+    assert_eq!(registered_node_provider_result, Ok(()));
+}
+
 #[test]
 fn test_canister_and_function_no_unreachable() {
     use strum::IntoEnumIterator;
```

### rs/nns/governance/unreleased_changelog.md
```diff
@@ -17,4 +17,8 @@ on the process that this file is part of, see
 
 ## Fixed
 
+* `validate_assign_noid_payload` no longer panics when a node provider has
+  `id = None`. It now skips such providers safely, preventing all
+  `AddNodeOperator` proposal submissions from being blocked.
+
 ## Security
```
