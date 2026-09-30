# [?] fix(gateway): contain panics on the iroh api path

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/4fd2d7a5c49582fae0ec8b01701a66ba530fe1cb
Type: security-commit

## Details
fix(gateway): contain panics on the iroh api path

There was no `catch_unwind` anywhere in the gateway. Iroh requests are
spawned with `spawn_cancellable_silent` on the gateway's root task group,
so a panicking handler drops `TaskPanicGuard` with `completed == false`,
which shuts the task group down, returns from `Gateway::run` and exits
the process. Deployments run the gateway under `restart: unless-stopped`,
so a request that panics deterministically is a boot loop rather than a
single crash.

The exposure is public: the docker compose file binds the iroh listener
to `0.0.0.0:8177` and publishes the port, and the gateway's node id is
announced to every federation it serves, so it is discoverable.

The HTTP path needs no equivalent change: `axum::serve` spawns its
connection tasks outside any task group, so a handler panic there only
drops that one connection.

Wrap the iroh handler invocation in `catch_unwind` and answer a 500,
mirroring what `fedimint-server`'s iroh path does.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9

## Patch
### gateway/fedimint-gateway-server/src/iroh_server.rs
```diff
@@ -1,4 +1,5 @@
 use std::collections::{BTreeMap, BTreeSet, HashMap};
+use std::panic::AssertUnwindSafe;
 use std::pin::Pin;
 use std::sync::Arc;
 
@@ -11,11 +12,12 @@ use fedimint_core::net::iroh::build_iroh_endpoint;
 use fedimint_core::task::TaskGroup;
 use fedimint_gateway_common::STOP_ENDPOINT;
 use fedimint_logging::LOG_GATEWAY;
+use futures::FutureExt as _;
 use iroh::endpoint::Incoming;
 use reqwest::StatusCode;
 use serde::de::DeserializeOwned;
 use serde_json::json;
-use tracing::info;
+use tracing::{error, info};
 use url::Url;
 
 use crate::Gateway;
@@ -198,11 +200,14 @@ async fn handle_incoming_iroh_request(
         let request = recv.read_to_end(100_000).await?;
         let request = serde_json::from_slice::<IrohGatewayRequest>(&request)?;
 
-        let (status, body) = handle_request(
-            &request,
-            gateway.clone(),
-            handlers.clone(),
-            task_group.clone(),
+        let (status, body) = run_handler(
+            &request.route,
+            handle_request(
+                &request,
+                gateway.clone(),
+                handlers.clone(),
+                task_group.clone(),
+            ),
         )
         .await?;
 
@@ -218,6 +223,35 @@ async fn handle_incoming_iroh_request(
     Ok(())
 }
 
+/// Runs a request handler, turning a panic into a 500 response for the caller
+/// that triggered it.
+///
+/// Iroh requests are spawned on the gateway's root task group, so a panic
+/// escaping a handler trips the task group's panic guard and shuts the whole
+/// gateway down. The HTTP path does not need this: `axum::serve` spawns its
+/// connection tasks outside any task group, so a panic there only drops that
+/// one connection.
+async fn run_handler(
+    route: &str,
+    handler: impl Future<Output = anyhow::Result<(StatusCode, Json<serde_json::Value>)>>,
+) -> anyhow::Result<(StatusCode, Json<serde_json::Value>)> {
+    // Using `AssertUnwindSafe` here is far from ideal. In theory this means we
+    // could end up with an inconsistent state. In practice this is only the last
+    // line of defense, and losing the gateway process entirely is strictly worse.
+    AssertUnwindSafe(handler)
+        .catch_unwind()
+        .await
+        .unwrap_or_else(|_| {
+            error!(
+                target: LOG_GATEWAY,
+                route,
+                "Gateway API handler panicked, DO NOT IGNORE, FIX IT!!!"
+            );
+
+            Ok((StatusCode::INTERNAL_SERVER_ERROR, Json(json!(()))))
+        })
+}
+
 /// Checks if the requested route is authenticated and will reject the request
 /// if the authentication is incorrect. Then it will lookup the specific handler
 /// in `Handlers`, execute it, and return the function's JSON along with an HTTP
@@ -299,3 +333,17 @@ fn iroh_verify_password(
 
     Err(anyhow!("Invalid password"))
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[tokio::test]
+    async fn panicking_handler_returns_an_error_instead_of_unwinding() {
+        let (status, _body) = run_handler("/pay_invoice", async { panic!("handler panic") })
+            .await
+            .expect("a panicking handler is contained");
+
+        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
+    }
+}
```
