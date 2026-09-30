# [?] Fix panic when querying connections filtered by counterparty chain (#3381)

## Summary
Severity: Unknown
Chain: Cosmos
Component: informalsystems/hermes
Published: 2023-06-05
Source: https://github.com/informalsystems/hermes/commit/5788c02f8000166162b3393a902bd9e87e3c25a5
Type: security-commit

## Details
Fix panic when querying connections filtered by counterparty chain (#3381)

* Fix panic when querying connections filtered by counterparty chain id

* Add changelog entry

## Patch
### .changelog/unreleased/bug-fixes/3381-panic-query-conns.md
```diff
@@ -0,0 +1,3 @@
+- Fix panic which can occur when querying connections filtered
+  by counterparty chain using `hermes query connections`
+  ([\#3381](https://github.com/informalsystems/hermes/issues/3381))
\ No newline at end of file
```

### crates/relayer-cli/src/commands/query/connections.rs
```diff
@@ -45,44 +45,37 @@ impl Runnable for QueryConnectionsCmd {
         let chain = spawn_chain_runtime(&config, &self.chain_id)
             .unwrap_or_else(exit_with_unrecoverable_error);
 
-        let res = chain.query_connections(QueryConnectionsRequest {
-            pagination: Some(PageRequest::all()),
-        });
-
-        let connections = match res {
-            Ok(connections) => {
-                // Check the counterparty chain id only if filtering is required.
-                if let Some(counterparty_filter_id) = self.counterparty_chain_id.clone() {
-                    let mut output = connections.clone();
-
-                    for (id, connection) in connections.into_iter().enumerate() {
-                        let client_id = connection.end().client_id().to_owned();
-                        let chain_height = chain.query_latest_height();
-                        let (client_state, _) = chain
-                            .query_client_state(
-                                QueryClientStateRequest {
-                                    client_id,
-                                    height: QueryHeight::Specific(chain_height.unwrap()),
-                                },
-                                IncludeProof::No,
-                            )
-                            .unwrap();
-                        let counterparty_chain_id = client_state.chain_id();
-
-                        if counterparty_chain_id != counterparty_filter_id {
-                            output.remove(id);
-                        }
-                    }
-                    output
-                } else {
-                    connections
-                }
-            }
-            Err(e) => Output::error(format!(
-                "An error occurred trying to query connections: {e}"
-            ))
-            .exit(),
-        };
+        let mut connections = chain
+            .query_connections(QueryConnectionsRequest {
+                pagination: Some(PageRequest::all()),
+            })
+            .unwrap_or_else(|e| {
+                Output::error(format!(
+                    "An error occurred trying to query connections: {e}"
+                ))
+                .exit()
+            });
+
+        // Check the counterparty chain id only if filtering is required.
+        if let Some(counterparty_filter_id) = self.counterparty_chain_id.clone() {
+            connections.retain(|connection| {
+                let client_id = connection.end().client_id().to_owned();
+                let chain_height = chain.query_latest_height();
+                let (client_state, _) = chain
+                    .query_client_state(
+                        QueryClientStateRequest {
+                            client_id,
+                            height: QueryHeight::Specific(chain_height.unwrap()),
+                        },
+                        IncludeProof::No,
+                    )
+                    .unwrap();
+
+                let counterparty_chain_id = client_state.chain_id();
+
+                counterparty_chain_id == counterparty_filter_id
+            });
+        }
 
         if self.verbose {
             Output::success(connections).exit()
```
