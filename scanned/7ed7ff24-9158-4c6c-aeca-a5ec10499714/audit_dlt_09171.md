# [?] server/index: Fix panic

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2020-05-11
Source: https://github.com/graphprotocol/graph-node/commit/1eeaaf8b1e84ffa29a8880499a2889c0f8fd9766
Type: security-commit

## Details
server/index: Fix panic

## Patch
### server/index-node/src/resolver.rs
```diff
@@ -338,47 +338,24 @@ where
                 .api_schema(&SUBGRAPHS_ID)
                 .map_err(QueryExecutionError::StoreError)?,
             // We're querying all deployments that match the provided filter
-            q::parse_query(
+            q::parse_query(&format!(
+                "{}{}",
+                DEPLOYMENT_STATUS_FRAGMENT,
                 r#"
                 query deployments(
                   $whereDeployments: SubgraphDeployment_filter!,
                   $whereAssignments: SubgraphDeploymentAssignment_filter!
                 ) {
                   subgraphDeployments(where: $whereDeployments, first: 1000000) {
-                    id
-                    synced
-                    health
-                    fatalError {
-                        message
-                        blockNumber
-                        blockHash
-                        handler
-                    }
-                    nonFatalErrors(first: 1000, orderBy: blockNumber) {
-                        message
-                        blockNumber
-                        blockHash
-                        handler
-                    }
-                    ethereumHeadBlockNumber
-                    ethereumHeadBlockHash
-                    earliestEthereumBlockHash
-                    earliestEthereumBlockNumber
-                    latestEthereumBlockHash
-                    latestEthereumBlockNumber
-                    manifest {
-                      dataSources(first: 1) {
-                        network
-                      }
-                    }
+                    ...deploymentStatus
                   }
                   subgraphDeploymentAssignments(where: $whereAssignments, first: 1000000) {
                     id
                     nodeId
                   }
                 }
                 "#,
-            )
+            ))
             .unwrap(),
             // If the `subgraphs` argument was provided, build a suitable `where`
             // filter to match the IDs; otherwise leave the `where` filter empty
@@ -441,38 +418,15 @@ where
                 .api_schema(&SUBGRAPHS_ID)
                 .map_err(QueryExecutionError::StoreError)?,
             // We're querying all deployments that match the provided filter
-            q::parse_query(
+            q::parse_query(&format!(
+                "{}{}",
+                DEPLOYMENT_STATUS_FRAGMENT,
                 r#"
                 query subgraphs($where: Subgraph_filter!) {
                   subgraphs(where: $where, first: 1000000) {
                     versions(orderBy: createdAt, orderDirection: asc, first: 1000000) {
                       deployment {
-                        id
-                        synced
-                        health
-                        fatalError {
-                            message
-                            blockNumber
-                            blockHash
-                            handler
-                        }
-                        nonFatalErrors(first: 1000, orderBy: blockNumber) {
-                            message
-                            blockNumber
-                            blockHash
-                            handler
-                        }
-                        ethereumHeadBlockNumber
-                        ethereumHeadBlockHash
-                        earliestEthereumBlockHash
-                        earliestEthereumBlockNumber
-                        latestEthereumBlockHash
-                        latestEthereumBlockNumber
-                        manifest {
-                          dataSources(first: 1) {
-                            network
-                          }
-                        }
+                       ...deploymentStatus
                       }
                     }
                   }
@@ -482,7 +436,7 @@ where
                   }
                 }
                 "#,
-            )
+            ))
             .unwrap(),
             // If the `subgraphs` argument was provided, build a suitable `where`
             // filter to match the IDs; otherwise leave the `where` filter empty
```
