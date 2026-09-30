# [?] Fix panic when Executor is used with dev mode (#1562)

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2024-03-18
Source: https://github.com/risc0/risc0/commit/8a42c07a24dae9715e42661cba31ddc9a02ccaae
Type: security-commit

## Details
Fix panic when Executor is used with dev mode (#1562)

I ran into an issue where, in using `risc0-zkvm` with the `client`
feature and `RISC0_DEV_MODE=1` I would get a panic. I tracked this down
to the way null segment refs were being handled, which is that deep
within the executor the provided callback was being ignored in dev mode.
I believe the root cause of the panic then was that dev mode was being
checked for at the wrong layer of abstraction.

In this PR, the decision on using `NullSegmentRef` is moved by have the
dev mode `ProverServer` implementation use `null_callback` in
`prove_with_context`. Additionally, the `LocalProver` impl of `Executor`
is altered to avoid calling `resolve` on the segments such that they
never need to be stored, and we are still able to construct the
`SessionInfo`.

This PR also cleans up some links that cause `cargo doc -Fclient` to
fail, and prunes `EmptySegmentRef`, which is redundant to
`NullSegmentRef` and not exported anywhere.

## Patch
### risc0/zkvm/src/host/api/server.rs
```diff
@@ -21,31 +21,22 @@ use std::{
 use anyhow::{anyhow, bail, Result};
 use bytes::Bytes;
 use prost::Message;
-use serde::{Deserialize, Serialize};
 
 use super::{malformed_err, path_to_string, pb, ConnectionWrapper, Connector, TcpConnector};
 use crate::{
     get_prover_server, get_version,
-    host::{client::slice_io::SliceIo, recursion::SuccinctReceipt},
+    host::{
+        client::slice_io::SliceIo, recursion::SuccinctReceipt, server::session::NullSegmentRef,
+    },
     receipt_claim::{MaybePruned, ReceiptClaim},
-    ExecutorEnv, ExecutorImpl, ProverOpts, Receipt, Segment, SegmentReceipt, SegmentRef,
-    TraceCallback, TraceEvent, VerifierContext,
+    ExecutorEnv, ExecutorImpl, ProverOpts, Receipt, Segment, SegmentReceipt, TraceCallback,
+    TraceEvent, VerifierContext,
 };
 
 /// A server implementation for handling requests by clients of the zkVM.
 pub struct Server {
     connector: Box<dyn Connector>,
 }
-
-#[derive(Clone, Serialize, Deserialize)]
-struct EmptySegmentRef;
-
-impl SegmentRef for EmptySegmentRef {
-    fn resolve(&self) -> Result<Segment> {
-        Err(anyhow!("Segment resolution not supported"))
-    }
-}
-
 struct PosixIoProxy {
     fd: u32,
     conn: ConnectionWrapper,
@@ -309,7 +300,7 @@ impl Server {
                     bail!(err)
                 }
 
-                Ok(Box::new(EmptySegmentRef))
+                Ok(Box::new(NullSegmentRef))
             })?;
 
             Ok(pb::api::ServerReply {
```

### risc0/zkvm/src/host/client/prove/local.rs
```diff
@@ -16,8 +16,8 @@ use anyhow::Result;
 
 use super::{Executor, Prover, ProverOpts};
 use crate::{
-    get_prover_server, ExecutorEnv, ExecutorImpl, Receipt, SegmentInfo, SessionInfo,
-    VerifierContext,
+    get_prover_server, host::server::session::NullSegmentRef, ExecutorEnv, ExecutorImpl, Receipt,
+    SegmentInfo, SessionInfo, VerifierContext,
 };
 
 /// A [Prover] implementation that selects a [crate::ProverServer] by calling
@@ -54,15 +54,14 @@ impl Prover for LocalProver {
 impl Executor for LocalProver {
     fn execute(&self, env: ExecutorEnv<'_>, elf: &[u8]) -> Result<SessionInfo> {
         let mut exec = ExecutorImpl::from_elf(env, elf)?;
-        let session = exec.run()?;
         let mut segments = Vec::new();
-        for segment in session.segments {
-            let segment = segment.resolve()?;
+        let session = exec.run_with_callback(|segment| {
             segments.push(SegmentInfo {
                 po2: segment.inner.po2 as u32,
                 cycles: segment.inner.insn_cycles as u32,
-            })
-        }
+            });
+            Ok(Box::new(NullSegmentRef))
+        })?;
         Ok(SessionInfo {
             segments,
             journal: session.journal.unwrap_or_default().into(),
```

### risc0/zkvm/src/host/client/prove/mod.rs
```diff
@@ -132,7 +132,7 @@ impl ProverOpts {
 /// The `RISC0_PROVER` environment variable, if specified, will select the
 /// following [Prover] implementation:
 /// * `bonsai`: [BonsaiProver] to prove on Bonsai.
-/// * `local`: [local::LocalProver] to prove locally in-process. Note: this
+/// * `local`: LocalProver to prove locally in-process. Note: this
 ///   requires the `prove` feature flag.
 /// * `ipc`: [ExternalProver] to prove using an `r0vm` sub-process. Note: `r0vm`
 ///   must be installed. To specify the path to `r0vm`, use `RISC0_SERVER_PATH`.
@@ -141,7 +141,7 @@ impl ProverOpts {
 /// [Prover]:
 /// * [BonsaiProver] if the `BONSAI_API_URL` and `BONSAI_API_KEY` environment
 ///   variables are set unless `RISC0_DEV_MODE` is enabled.
-/// * [local::LocalProver] if the `prove` feature flag is enabled.
+/// * LocalProver if the `prove` feature flag is enabled.
 /// * [ExternalProver] otherwise.
 pub fn default_prover() -> Rc<dyn Prover> {
     let explicit = std::env::var("RISC0_PROVER").unwrap_or_default();
@@ -175,15 +175,15 @@ pub fn default_prover() -> Rc<dyn Prover> {
 ///
 /// The `RISC0_EXECUTOR` environment variable, if specified, will select the
 /// following [Executor] implementation:
-/// * `local`: [local::LocalProver] to execute locally in-process. Note: this is
+/// * `local`: LocalProver to execute locally in-process. Note: this is
 ///   only available when the `prove` feature is enabled.
 /// * `ipc`: [ExternalProver] to execute using an `r0vm` sub-process. Note:
 ///   `r0vm` must be installed. To specify the path to `r0vm`, use
 ///   `RISC0_SERVER_PATH`.
 ///
 /// If `RISC0_EXECUTOR` is not specified, the following rules are used to select
 /// an [Executor]:
-/// * [local::LocalProver] if the `prove` feature flag is enabled.
+/// * LocalProver if the `prove` feature flag is enabled.
 /// * [ExternalProver] otherwise.
 pub fn default_executor() -> Rc<dyn Executor> {
     let explicit = std::env::var("RISC0_EXECUTOR").unwrap_or_default();
```

### risc0/zkvm/src/host/server/exec/executor.rs
```diff
@@ -29,9 +29,8 @@ use risc0_zkvm_platform::{fileno, memory::GUEST_MAX_MEM, PAGE_SIZE};
 use tempfile::tempdir;
 
 use crate::{
-    host::{client::env::SegmentPath, server::session::null_callback},
-    is_dev_mode, Assumption, Assumptions, ExecutorEnv, FileSegmentRef, Output, Segment, SegmentRef,
-    Session,
+    host::client::env::SegmentPath, Assumption, Assumptions, ExecutorEnv, FileSegmentRef, Output,
+    Segment, SegmentRef, Session,
 };
 
 use super::{
@@ -123,11 +122,6 @@ impl<'a> ExecutorImpl<'a> {
     where
         F: FnMut(Segment) -> Result<Box<dyn SegmentRef>>,
     {
-        let mut callback = |segment| match is_dev_mode() {
-            true => null_callback(),
-            false => callback(segment),
-        };
-
         let journal = Journal::default();
         self.env
             .posix_io
@@ -141,7 +135,6 @@ impl<'a> ExecutorImpl<'a> {
 
         let mut refs = Vec::new();
         let mut exec = Executor::new(self.image.clone(), self, self.env.trace.clone());
-        let is_dev_mode = is_dev_mode();
 
         let start_time = Instant::now();
         let result = exec.run(segment_limit_po2, self.env.session_limit, |inner| {
@@ -183,11 +176,7 @@ impl<'a> ExecutorImpl<'a> {
                 inner,
                 output,
             };
-            let segment_ref = if is_dev_mode {
-                null_callback()?
-            } else {
-                callback(segment.into())?
-            };
+            let segment_ref = callback(segment.into())?;
             refs.push(segment_ref);
             Ok(())
         })?;
```

### risc0/zkvm/src/host/server/prove/dev_mode.rs
```diff
@@ -15,8 +15,11 @@
 use anyhow::{bail, Result};
 
 use crate::{
-    host::receipt::{InnerReceipt, SegmentReceipt, SuccinctReceipt},
-    ProverServer, Receipt, Segment, Session, VerifierContext,
+    host::{
+        receipt::{InnerReceipt, SegmentReceipt, SuccinctReceipt},
+        server::session::null_callback,
+    },
+    ExecutorEnv, ExecutorImpl, ProverServer, Receipt, Segment, Session, VerifierContext,
 };
 
 /// An implementation of a [ProverServer] for development and testing purposes.
@@ -60,6 +63,18 @@ impl ProverServer for DevModeProver {
         ))
     }
 
+    /// Prove the specified ELF binary using the specified [VerifierContext].
+    fn prove_with_ctx(
+        &self,
+        env: ExecutorEnv<'_>,
+        ctx: &VerifierContext,
+        elf: &[u8],
+    ) -> Result<Receipt> {
+        let mut exec = ExecutorImpl::from_elf(env, elf)?;
+        let session = exec.run_with_callback(null_callback)?;
+        self.prove_session(ctx, &session)
+    }
+
     fn prove_segment(&self, _ctx: &VerifierContext, _segment: &Segment) -> Result<SegmentReceipt> {
         unimplemented!("This is unsupported for dev mode.")
     }
```

### risc0/zkvm/src/host/server/session.rs
```diff
@@ -212,22 +212,20 @@ impl Session {
     }
 }
 
-const NULL_SEGMENT_REF: NullSegmentRef = NullSegmentRef {};
-
 /// Implementation of a [SegmentRef] that does not save the segment.
 ///
 /// This is useful for DevMode where the segments aren't needed.
 #[derive(Serialize, Deserialize)]
-pub struct NullSegmentRef {}
+pub struct NullSegmentRef;
 
 impl SegmentRef for NullSegmentRef {
     fn resolve(&self) -> anyhow::Result<Segment> {
         unimplemented!()
     }
 }
 
-pub fn null_callback() -> Result<Box<dyn SegmentRef>> {
-    Ok(Box::new(NULL_SEGMENT_REF))
+pub fn null_callback(_: Segment) -> Result<Box<dyn SegmentRef>> {
+    Ok(Box::new(NullSegmentRef))
 }
 
 /// A very basic implementation of a [SegmentRef].
```
