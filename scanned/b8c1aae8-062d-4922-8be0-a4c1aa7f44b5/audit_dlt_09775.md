# [?] Address `async-graphql` vulnerability (#2290)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-10-04
Source: https://github.com/FuelLabs/fuel-core/commit/a932dadc1bc7cec75c7d882747ebfa0907373449
Type: security-commit

## Details
Address `async-graphql` vulnerability (#2290)

## Patch
### CHANGELOG.md
```diff
@@ -7,6 +7,7 @@ and this project adheres to [Semantic Versioning](http://semver.org/).
 ## [Unreleased]
 
 ### Added
+- [2290](https://github.com/FuelLabs/fuel-core/pull/2290): Added a new CLI argument `--graphql-max-directives`. The default value is `10`.
 - [2195](https://github.com/FuelLabs/fuel-core/pull/2195): Added enforcement of the limit on the size of the L2 transactions per block according to the `block_transaction_size_limit` parameter.
 - [2131](https://github.com/FuelLabs/fuel-core/pull/2131): Add flow in TxPool in order to ask to newly connected peers to share their transaction pool
 - [2182](https://github.com/FuelLabs/fuel-core/pull/2151): Limit number of transactions that can be fetched via TxSource::next
@@ -18,6 +19,7 @@ and this project adheres to [Semantic Versioning](http://semver.org/).
 ### Changed
 
 #### Breaking
+- [2290](https://github.com/FuelLabs/fuel-core/pull/2290): Added a new GraphQL limit on number of `directives`. The default value is `10`.
 - [2206](https://github.com/FuelLabs/fuel-core/pull/2206): Use timestamp of last block when dry running transactions.
 - [2153](https://github.com/FuelLabs/fuel-core/pull/2153): Updated default gas costs for the local testnet configuration to match `fuel-core 0.35.0`.
 
```

### bin/fuel-core/src/cli/run.rs
```diff
@@ -442,6 +442,7 @@ impl Command {
                 max_queries_depth: graphql.graphql_max_depth,
                 max_queries_complexity: graphql.graphql_max_complexity,
                 max_queries_recursive_depth: graphql.graphql_max_recursive_depth,
+                max_queries_directives: graphql.max_queries_directives,
                 request_body_bytes_limit: graphql.graphql_request_body_bytes_limit,
                 api_request_timeout: graphql.api_request_timeout.into(),
                 query_log_threshold_time: graphql.query_log_threshold_time.into(),
```

### bin/fuel-core/src/cli/run/graphql.rs
```diff
@@ -24,6 +24,10 @@ pub struct GraphQLArgs {
     #[clap(long = "graphql-max-recursive-depth", default_value = "16", env)]
     pub graphql_max_recursive_depth: usize,
 
+    /// The max number of directives in the query.
+    #[clap(long = "graphql-max-directives", default_value = "10", env)]
+    pub max_queries_directives: usize,
+
     /// The max body limit of the GraphQL query.
     #[clap(
         long = "graphql-request-body-bytes-limit",
```

### crates/fuel-core/Cargo.toml
```diff
@@ -12,7 +12,7 @@ version = { workspace = true }
 
 [dependencies]
 anyhow = { workspace = true }
-async-graphql = { version = "7.0.6", features = [
+async-graphql = { version = "7.0.11", features = [
   "playground",
   "tracing",
 ], default-features = false }
```

### crates/fuel-core/src/graphql_api.rs
```diff
@@ -21,6 +21,7 @@ pub struct ServiceConfig {
     pub max_queries_depth: usize,
     pub max_queries_complexity: usize,
     pub max_queries_recursive_depth: usize,
+    pub max_queries_directives: usize,
     pub request_body_bytes_limit: usize,
     /// Time to wait after submitting a query before debug info will be logged about query.
     pub query_log_threshold_time: Duration,
```

### crates/fuel-core/src/graphql_api/api_service.rs
```diff
@@ -202,6 +202,7 @@ where
         .limit_complexity(config.config.max_queries_complexity)
         .limit_depth(config.config.max_queries_depth)
         .limit_recursive_depth(config.config.max_queries_recursive_depth)
+        .limit_directives(config.config.max_queries_directives)
         .extension(MetricsExtension::new(
             config.config.query_log_threshold_time,
         ))
```

### crates/fuel-core/src/service/config.rs
```diff
@@ -136,6 +136,7 @@ impl Config {
                 max_queries_depth: 16,
                 max_queries_complexity: 20000,
                 max_queries_recursive_depth: 16,
+                max_queries_directives: 10,
                 request_body_bytes_limit: 16 * 1024 * 1024,
                 query_log_threshold_time: Duration::from_secs(2),
                 api_request_timeout: Duration::from_secs(60),
```
