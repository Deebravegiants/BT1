# [?] [sc-rpc-server] Fix panic while dropping the RPC runtime on start_ser… (#12847)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-08-12
Source: https://github.com/paritytech/polkadot-sdk/commit/f209831c0e48bf1a3462199e65f17ff6aa68ec13
Type: security-commit

## Details
[sc-rpc-server] Fix panic while dropping the RPC runtime on start_ser… (#12847)

# Description

`start_server` panicked instead of returning its error on both of its
failure
paths, masking the underlying cause. An operator who pins
`--rpc-endpoint` to a
port that is already in use saw a tokio runtime panic rather than
"Address already in use".

The dedicated RPC `tokio::runtime::Runtime` is now held in a guard for
the
duration of `start_server`, so every exit path shuts it down with
`shutdown_background()` and the original error reaches the caller.

Closes #12785

## Integration

No public API change — `RuntimeGuard` is private and `start_server`'s
signature
is unchanged, so downstream code needs no modification. `sc-rpc-server`
takes a
`patch` bump.

There is one behavioural change worth knowing about. Previously, a
non-optional
endpoint that failed to bind (or all endpoints failing) aborted the
process with
a tokio panic. Now the error propagates normally, so
`sc_service::start_rpc_servers` returns `Err` and the node fails to
start with a
readable message instead of a panic. Anything that was (accidentally)
relying on
the process dying at that point will now see a `Result` it must handle —
in
practice this only affects the error message operators see.

A `[dev-dependencies]` entry on `tokio` (`macros`, `net`,
`rt-multi-thread`) was
added so the new tests can use `#[tokio::test]`. Build-time only.

## Review Notes

`start_server` destructures `Config`, which moves the runtime into a
plain local
binding. The two exits then diverge:

- **Success**: the runtime is moved into `Server`, whose `Drop` already
tears it
  down with `shutdown_background()`, with a comment explaining why.
- **Errors** (`Err(e) => return Err(e)` for a non-optional bind failure,
and
`return Err(Box::new(ListenAddrError))` when nothing bound): the runtime
is
moved nowhere, so drop glue runs at scope exit. `Runtime::drop` blocks
until
  the blocking pool joins, and `start_server` is awaited inside
  `Handle::block_on`, where tokio forbids blocking.

The backtrace confirms this — it points at the closing brace of
`start_server`,
not at any statement, because the drop is compiler-generated.

Both error paths are correct Rust in isolation. The bug is the
asymmetry: the
success path routes the runtime through a type that knows about the
hazard, and
nothing forces the error paths to do the same. Hence a guard rather than
two
patched `return`s:

```diff
-     let rpc_handle = rpc_runtime.handle().clone();
+     let rpc_runtime = RuntimeGuard::new(rpc_runtime);
+     let rpc_handle = rpc_runtime.handle();

      // ... both early returns now drop the guard -> shutdown_background()

-     Ok(Server::new(server_handle, local_addrs, rpc_runtime))
+     Ok(Server::new(server_handle, local_addrs, rpc_runtime.into_inner()))
```
On success into_inner() takes the runtime out, leaving the guard holding
None so its Drop is a no-op and Server owns it as before.

Alternative considered. Calling rpc_runtime.shutdown_background() before
each of the two returns is ~4 lines instead of ~30, and compiles fine
(the
move sits on a diverging path). I chose the guard because nothing
enforces that
a future early return remembers those lines, and this bug exists
precisely
because a return was added without considering the runtime. Happy to
switch to
the smaller diff if reviewers prefer it.

<details>
<summary>Why <code>shutdown_background()</code> does not leak the
server</summary>

shutdown_background() is shutdown_timeout(Duration::from_nanos(0)):
```
pub fn shutdown_timeout(mut self, duration: Duration) {
    self.handle.inner.shutdown();                 // shuts the scheduler down
    self.blocking_pool.shutdown(Some(duration));  // this is the "don't wait" part
}
```
The scheduler is still shut down; only the wait on the blocking pool is
skipped.
Two tokio details make this safe where a plain drop is not:
Receiver::wait
early-returns on a zero timeout before reaching the panic check, and
BlockingPool::shutdown is idempotent via its shared.shutdown flag, so
the
subsequent real Drop returns immediately instead of blocking.

Independently, server_handle is dropped on the error path, and
StopHandle:: shutdown() resolves when all watch senders drop, so every
already-spawned accept loop breaks out and releases its listener.


</details>

Testing

Adds the first #[cfg(test)] module in lib.rs covering both error paths.
Both panic before the fix
and pass after it:

SKIP_WASM_BUILD=1 cargo test -p sc-rpc-server --lib

Checklist

- [x] My PR includes a detailed description as outlined in the
"Description" and its two
- [x] My PR follows the labeling requirements
(https://github.com/paritytech/polkadot-sdk/blob/master/docs/contributor/CONTRIBUTING.md#Process)
of this project (at minimum one label for T required)
  - External contributors: Use /cmd label <label-name> to add labels
  - Maintainers can also add labels manually
- [x] I have made corresponding changes to the documentation (if
applicable)
- [x] I have added tests that prove my fix is effective or that my
feature works (if applicable)

---------

Co-authored-by: Dmitry Markin <dmitry@markin.tech>

### prdoc/pr_12847.prdoc
```diff
@@ -0,0 +1,18 @@
+title: Fix panic on `sc-rpc-server` `start_server` error paths
+
+doc:
+- audience: [Node Dev, Node Operator]
+  description: |-
+    `start_server` took ownership of the dedicated RPC `tokio::runtime::Runtime` and dropped it as
+    an ordinary local on its two error paths (a non-optional endpoint failing to bind, and no
+    listen address). Since `start_server` is awaited from within a runtime
+    context, that drop panicked with "Cannot drop a runtime in a context where blocking is not
+    allowed", masking the underlying error.
+
+    The runtime is now held in a guard for the duration of `start_server`, so every exit path
+    shuts it down with `shutdown_background()`, the same approach `Server::drop` already used,
+    and the original error is returned to the caller instead of being replaced by a panic.
+
+crates:
+- name: sc-rpc-server
+  bump: patch
```

### substrate/client/rpc-servers/Cargo.toml
```diff
@@ -36,3 +36,6 @@ sp-core = { workspace = true }
 tokio = { features = ["parking_lot"], workspace = true, default-features = true }
 tower = { workspace = true, features = ["util"] }
 tower-http = { workspace = true, features = ["cors"] }
+
+[dev-dependencies]
+tokio = { features = ["macros", "net", "rt-multi-thread"], workspace = true }
```

### substrate/client/rpc-servers/src/lib.rs
```diff
@@ -190,6 +190,42 @@ pub struct Config<M: Send + Sync + 'static> {
 	pub rpc_runtime: tokio::runtime::Runtime,
 }
 
+/// Guards the dedicated RPC runtime while [`start_server`] is setting the server up.
+///
+/// `start_server` is awaited from within a runtime context, so dropping the RPC runtime on an
+/// early error return would panic: `Runtime::drop` blocks until the blocking pool has shut down,
+/// which tokio forbids on a runtime thread. Routing every exit path through this guard tears the
+/// runtime down with `shutdown_background()` instead, just like [`Server::drop`] does.
+struct RuntimeGuard(Option<tokio::runtime::Runtime>);
+
+impl RuntimeGuard {
+	fn new(runtime: tokio::runtime::Runtime) -> Self {
+		Self(Some(runtime))
+	}
+
+	fn handle(&self) -> tokio::runtime::Handle {
+		self.0
+			.as_ref()
+			.expect("runtime is only taken in `into_inner` and `Drop`; qed")
+			.handle()
+			.clone()
+	}
+
+	/// Hands the runtime over to the [`Server`], which owns it from then on.
+	fn into_inner(mut self) -> tokio::runtime::Runtime {
+		self.0.take().expect("runtime is only taken here and in `Drop`; qed")
+	}
+}
+
+impl Drop for RuntimeGuard {
+	fn drop(&mut self) {
+		if let Some(runtime) = self.0.take() {
+			// Same trade-off `Server::drop` accepts
+			runtime.shutdown_background();
+		}
+	}
+}
+
 #[derive(Debug, Clone)]
 struct PerConnection {
 	methods: Methods,
@@ -206,7 +242,9 @@ where
 	let Config { endpoints, metrics, rpc_api, id_provider, request_logger_limit, rpc_runtime } =
 		config;
 
-	let rpc_handle = rpc_runtime.handle().clone();
+	// Held as a guard so that every early error return below shuts the runtime down
+	let rpc_runtime = RuntimeGuard::new(rpc_runtime);
+	let rpc_handle = rpc_runtime.handle();
 
 	let (stop_handle, server_handle) = stop_channel();
 	let cfg = PerConnection {
@@ -393,5 +431,63 @@ where
 	// This is to make it work with old scripts/utils that parse the logs.
 	log::info!("Running JSON-RPC server: addr={}", format_listen_addrs(&local_addrs));
 
-	Ok(Server::new(server_handle, local_addrs, rpc_runtime))
+	Ok(Server::new(server_handle, local_addrs, rpc_runtime.into_inner()))
+}
+
+#[cfg(test)]
+mod tests {
+	use super::*;
+
+	fn test_runtime() -> tokio::runtime::Runtime {
+		tokio::runtime::Builder::new_multi_thread()
+			.worker_threads(1)
+			.enable_all()
+			.build()
+			.expect("test runtime can be built; qed")
+	}
+
+	fn config(endpoints: Vec<RpcEndpoint>) -> Config<()> {
+		Config {
+			endpoints,
+			metrics: None,
+			rpc_api: RpcModule::new(()),
+			id_provider: None,
+			request_logger_limit: 1024,
+			rpc_runtime: test_runtime(),
+		}
+	}
+
+	fn endpoint(listen_addr: SocketAddr) -> RpcEndpoint {
+		RpcEndpoint {
+			listen_addr,
+			batch_config: BatchRequestConfig::Disabled,
+			max_connections: 1,
+			max_payload_in_mb: 1,
+			max_payload_out_mb: 1,
+			max_subscriptions_per_connection: 1,
+			max_buffer_capacity_per_connection: 1,
+			rate_limit: None,
+			rate_limit_trust_proxy_headers: false,
+			rate_limit_whitelisted_ips: Vec::new(),
+			cors: None,
+			rpc_methods: RpcMethods::Auto,
+			is_optional: false,
+			retry_random_port: false,
+		}
+	}
+
+	#[tokio::test]
+	async fn start_server_with_no_endpoints_returns_error_without_panicking() {
+		let res = start_server(config(Vec::new())).await;
+		assert!(res.is_err(), "expected ListenAddrError, got Ok");
+	}
+
+	#[tokio::test]
+	async fn start_server_bind_failure_returns_error_without_panicking() {
+		let blocker = std::net::TcpListener::bind("127.0.0.1:0").expect("bind blocker; qed");
+		let taken_addr = blocker.local_addr().expect("blocker has a local addr; qed");
+
+		let res = start_server(config(vec![endpoint(taken_addr)])).await;
+		assert!(res.is_err(), "expected a bind error, got Ok");
+	}
 }
```
