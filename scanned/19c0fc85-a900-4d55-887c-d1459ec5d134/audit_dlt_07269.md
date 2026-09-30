# [?] fix: Update libp2p-websocket to v0.42.2 to fix panics (#5040)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2024-07-17
Source: https://github.com/paritytech/polkadot-sdk/commit/b862b181ec507e1510dff6d78335b184b395d9b2
Type: security-commit

## Details
fix: Update libp2p-websocket to v0.42.2 to fix panics (#5040)

This release includes: https://github.com/libp2p/rust-libp2p/pull/5482

Which fixes substrate node crashing with libp2p trace:

```
 0: sp_panic_handler::set::{{closure}}
   1: std::panicking::rust_panic_with_hook
   2: std::panicking::begin_panic::{{closure}}
   3: std::sys_common::backtrace::__rust_end_short_backtrace
   4: std::panicking::begin_panic
   5: <quicksink::SinkImpl<S,F,T,A,E> as futures_sink::Sink<A>>::poll_ready
   6: <rw_stream_sink::RwStreamSink<S> as futures_io::if_std::AsyncWrite>::poll_write
   7: <libp2p_noise::io::framed::NoiseFramed<T,S> as futures_sink::Sink<&alloc::vec::Vec<u8>>>::poll_ready
   8: <libp2p_noise::io::Output<T> as futures_io::if_std::AsyncWrite>::poll_write
   9: <yamux::frame::io::Io<T> as futures_sink::Sink<yamux::frame::Frame<()>>>::poll_ready
  10: yamux::connection::Connection<T>::poll_next_inbound
  11: <libp2p_yamux::Muxer<C> as libp2p_core::muxing::StreamMuxer>::poll
  12: <libp2p_core::muxing::boxed::Wrap<T> as libp2p_core::muxing::StreamMuxer>::poll
  13: <libp2p_core::muxing::boxed::Wrap<T> as libp2p_core::muxing::StreamMuxer>::poll
  14: libp2p_swarm::connection::pool::task::new_for_established_connection::{{closure}}
  15: <sc_service::task_manager::prometheus_future::PrometheusFuture<T> as core::future::future::Future>::poll
  16: <futures_util::future::select::Select<A,B> as core::future::future::Future>::poll
  17: <tracing_futures::Instrumented<T> as core::future::future::Future>::poll
  18: std::panicking::try
  19: tokio::runtime::task::harness::Harness<T,S>::poll
  20: tokio::runtime::scheduler::multi_thread::worker::Context::run_task
  21: tokio::runtime::scheduler::multi_thread::worker::Context::run
  22: tokio::runtime::context::set_scheduler
  23: tokio::runtime::context::runtime::enter_runtime
  24: tokio::runtime::scheduler::multi_thread::worker::run
  25: tokio::runtime::task::core::Core<T,S>::poll
  26: tokio::runtime::task::harness::Harness<T,S>::poll
  27: std::sys_common::backtrace::__rust_begin_short_backtrace
  28: core::ops::function::FnOnce::call_once{{vtable.shim}}
  29: std::sys::pal::unix::thread::Thread::new::thread_start
  30: <unknown>
  31: <unknown>


Thread 'tokio-runtime-worker' panicked at 'SinkImpl::poll_ready called after error.', /home/ubuntu/.cargo/registry/src/index.crates.io-6f17d22bba15001f/quicksink-0.1.2/src/lib.rs:158
```

Closes: https://github.com/paritytech/polkadot-sdk/issues/4934

---------

Signed-off-by: Alexandru Vasile <alexandru.vasile@parity.io>

## Patch
### Cargo.lock
```diff
@@ -1206,7 +1206,7 @@ checksum = "ff6e472cdea888a4bd64f342f09b3f50e1886d32afe8df3d663c01140b811b18"
 dependencies = [
  "event-listener 5.2.0",
  "event-listener-strategy",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
 ]
 
 [[package]]
@@ -1260,7 +1260,7 @@ dependencies = [
  "log",
  "memchr",
  "once_cell",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "pin-utils",
  "slab",
  "wasm-bindgen-futures",
@@ -1274,7 +1274,7 @@ checksum = "cd56dd203fef61ac097dd65721a419ddccb106b2d2b70ba60a6b529f03961a51"
 dependencies = [
  "async-stream-impl",
  "futures-core",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
 ]
 
 [[package]]
@@ -1315,7 +1315,7 @@ dependencies = [
  "futures-sink",
  "futures-util",
  "memchr",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
 ]
 
 [[package]]
@@ -5352,7 +5352,7 @@ checksum = "2b5fb89194fa3cad959b833185b3063ba881dbfc7030680b314250779fb4cc91"
 dependencies = [
  "concurrent-queue",
  "parking",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
 ]
 
 [[package]]
@@ -5362,7 +5362,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0f214dc438f977e6d4e3500aaa277f5ad94ca83fbbd9b1a15713ce2344ccc5a1"
 dependencies = [
  "event-listener 5.2.0",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
 ]
 
 [[package]]
@@ -5659,9 +5659,9 @@ dependencies = [
 
 [[package]]
 name = "form_urlencoded"
-version = "1.2.0"
+version = "1.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a62bc1cf6f830c2ec14a513a9fb124d0a213a629668a4186f329db21fe045652"
+checksum = "e13624c2627564efccf4934284bdd98cbaa14e79b0b5a141218e507b3a823456"
 dependencies = [
  "percent-encoding",
 ]
@@ -6231,7 +6231,7 @@ dependencies = [
  "futures-io",
  "memchr",
  "parking",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "waker-fn",
 ]
 
@@ -6242,7 +6242,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "52527eb5074e35e9339c6b4e8d12600c7128b68fb25dcb9fa9dec18f7c25f3a5"
 dependencies = [
  "futures-core",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
 ]
 
 [[package]]
@@ -6297,7 +6297,7 @@ dependencies = [
  "futures-sink",
  "futures-task",
  "memchr",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "pin-utils",
  "slab",
 ]
@@ -6755,7 +6755,7 @@ checksum = "d5f38f16d184e36f2408a55281cd658ecbd3ca05cce6d6510a176eca393e26d1"
 dependencies = [
  "bytes",
  "http 0.2.9",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
 ]
 
 [[package]]
@@ -6778,7 +6778,7 @@ dependencies = [
  "futures-util",
  "http 1.1.0",
  "http-body 1.0.0",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
 ]
 
 [[package]]
@@ -6815,7 +6815,7 @@ dependencies = [
  "httparse",
  "httpdate",
  "itoa",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "socket2 0.5.7",
  "tokio",
  "tower-service",
@@ -6838,7 +6838,7 @@ dependencies = [
  "httparse",
  "httpdate",
  "itoa",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "smallvec",
  "tokio",
  "want",
@@ -6890,7 +6890,7 @@ dependencies = [
  "http 1.1.0",
  "http-body 1.0.0",
  "hyper 1.3.1",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "socket2 0.5.7",
  "tokio",
  "tower",
@@ -6942,6 +6942,16 @@ dependencies = [
  "unicode-normalization",
 ]
 
+[[package]]
+name = "idna"
+version = "0.5.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "634d9b1461af396cad843f47fdba5597a4f9e6ddd4bfb6ff5d85028c25cb12f6"
+dependencies = [
+ "unicode-bidi",
+ "unicode-normalization",
+]
+
 [[package]]
 name = "if-addrs"
 version = "0.10.2"
@@ -8059,9 +8069,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-websocket"
-version = "0.42.1"
+version = "0.42.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3facf0691bab65f571bc97c6c65ffa836248ca631d631b7691ac91deb7fceb5f"
+checksum = "004ee9c4a4631435169aee6aad2f62e3984dc031c43b6d29731e8e82a016c538"
 dependencies = [
  "either",
  "futures",
@@ -8070,9 +8080,10 @@ dependencies = [
  "libp2p-identity",
  "log",
  "parking_lot 0.12.3",
- "quicksink",
+ "pin-project-lite",
  "rw-stream-sink",
- "soketto 0.7.1",
+ "soketto 0.8.0",
+ "thiserror",
  "url",
  "webpki-roots 0.25.2",
 ]
@@ -12589,9 +12600,9 @@ dependencies = [
 
 [[package]]
 name = "percent-encoding"
-version = "2.3.0"
+version = "2.3.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9b2a4787296e9989611394c33f193f676704af1686e70b8f8033ab5ba9a35a94"
+checksum = "e3148f5046208a5d56bcfc03053e3ca6334e51da8dfb19b6cdc8b306fae3283e"
 
 [[package]]
 name = "pest"
@@ -12669,15 +12680,9 @@ dependencies = [
 
 [[package]]
 name = "pin-project-lite"
-version = "0.1.12"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "257b64915a082f7811703966789728173279bdebb956b143dbcd23f6f970a777"
-
-[[package]]
-name = "pin-project-lite"
-version = "0.2.12"
+version = "0.2.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "12cc1b0bf1727a77a54b6654e7b5f1af8604923edc8b81885f8ec92f9e3f0a05"
+checksum = "bda66fc9667c18cb2758a2ac84d1167245054bcf85d5d1aaa6923f45801bdd02"
 
 [[package]]
 name = "pin-utils"
@@ -15072,7 +15077,7 @@ dependencies = [
  "concurrent-queue",
  "libc",
  "log",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "windows-sys 0.48.0",
 ]
 
@@ -15084,7 +15089,7 @@ checksum = "30054e72317ab98eddd8561db0f6524df3367636884b7b21b703e4b280a84a14"
 dependencies = [
  "cfg-if",
  "concurrent-queue",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "rustix 0.38.21",
  "tracing",
  "windows-sys 0.52.0",
@@ -15653,25 +15658,14 @@ dependencies = [
  "rand",
 ]
 
-[[package]]
-name = "quicksink"
-version = "0.1.2"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "77de3c815e5a160b1539c6592796801df2043ae35e123b46d73380cfa57af858"
-dependencies = [
- "futures-core",
- "futures-sink",
- "pin-project-lite 0.1.12",
-]
-
 [[package]]
 name = "quinn"
 version = "0.9.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2e8b432585672228923edbbf64b8b12c14e1112f62e88737655b4a083dbcd78e"
 dependencies = [
  "bytes",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "quinn-proto 0.9.6",
  "quinn-udp 0.3.2",
  "rustc-hash",
@@ -15690,7 +15684,7 @@ checksum = "8cc2c5017e4b43d5995dcea317bc46c1e09404c0a9664d2908f7f02dfe943d75"
 dependencies = [
  "bytes",
  "futures-io",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "quinn-proto 0.10.6",
  "quinn-udp 0.4.1",
  "rustc-hash",
@@ -16164,7 +16158,7 @@ dependencies = [
  "mime",
  "once_cell",
  "percent-encoding",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "rustls 0.21.7",
  "rustls-pemfile 1.0.3",
  "serde",
@@ -22063,7 +22057,7 @@ dependencies = [
  "mio",
  "num_cpus",
  "parking_lot 0.12.3",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "signal-hook-registry",
  "socket2 0.5.7",
  "tokio-macros",
@@ -22120,7 +22114,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "397c988d37662c7dda6d2208364a706264bf3d6138b11d436cbac0ad38832842"
 dependencies = [
  "futures-core",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "tokio",
  "tokio-util",
 ]
@@ -22163,7 +22157,7 @@ dependencies = [
  "futures-core",
  "futures-io",
  "futures-sink",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "tokio",
 ]
 
@@ -22230,7 +22224,7 @@ dependencies = [
  "futures-core",
  "futures-util",
  "pin-project",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "tokio",
  "tower-layer",
  "tower-service",
@@ -22248,7 +22242,7 @@ dependencies = [
  "http 1.1.0",
  "http-body 1.0.0",
  "http-body-util",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "tower-layer",
  "tower-service",
 ]
@@ -22272,7 +22266,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c3523ab5a71916ccf420eebdf5521fcef02141234bbc0b8a49f2fdc4544364ef"
 dependencies = [
  "log",
- "pin-project-lite 0.2.12",
+ "pin-project-lite",
  "tracing-attributes",
  "tracing-core",
 ]
@@ -22716,12 +22710,12 @@ checksum = "8ecb6da28b8a351d773b68d5825ac39017e680750f980f3a1a85cd8dd28a47c1"
 
 [[package]]
 name = "url"
-version = "2.4.0"
+version = "2.5.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "50bff7831e19200a85b17131d085c25d7811bc4e186efdaf54bbd132994a88cb"
+checksum = "22784dbdf76fdde8af1aeda5622b546b422b6fc585325248a2bf9f5e41e94d6c"
 dependencies = [
  "form_urlencoded",
- "idna 0.4.0",
+ "idna 0.5.0",
  "percent-encoding",
 ]
 
```

### prdoc/pr_5040.prdoc
```diff
@@ -0,0 +1,11 @@
+title: Update libp2p-websocket to v0.42.2
+
+doc:
+  - audience: Node Operator
+    description: |
+      Fixes a panic coming from the libp2p-websocket which stops the node.
+      This fix ensures that polling multiple time after error results in an error instead of panics.
+
+crates: 
+- name: sc-network
+  bump: minor
```
