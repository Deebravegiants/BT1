### Title
`enroll_user::make_signature` signs iris codes without checking `Pipeline.occlusion` / `face_identifier_fraud_checks` results, allowing signature generation and signup submission despite failed biometric fraud/occlusion signals - ([File: src/plans/enroll_user.rs])

### Summary
`biometric_pipeline()` in `src/plans/mod.rs` records occlusion and face-identifier failures only into `debug_report::Builder` (`occlusion_error`, `face_identifier_results`) for telemetry, but still returns `Ok(Some(pipeline))` regardless of whether `pipeline.occlusion` or `pipeline.face_identifier_fraud_checks` are `Err`. `detect_fraud()` is a no-op stub (`// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`) that unconditionally returns `Ok(false)`. `enroll_user::make_signature` then hashes and signs `pipeline.v2.eye_left/eye_right.iris_code`/`mask_code` via `secure_element::sign` without ever inspecting `pipeline.occlusion` or `pipeline.face_identifier_fraud_checks`.

### Finding Description
`biometric_pipeline()` (`src/plans/mod.rs:1290-1388`) runs the pipeline, then does: [1](#0-0) 
It forwards the occlusion/face-identifier outcomes only to the debug report builder for later telemetry serialization (`PipelineErrors.occlusion_error`, `face_identifier_error`), never gating the return value: [2](#0-1) 
`Ok(Some(pipeline))` is unconditionally produced as long as the earlier `match pipeline { Ok(pipeline) => pipeline, Err(e) => { ...; return Ok(None) } }` branch (which only catches `biometric_pipeline::Error::{Timeout, Agent, Iris}`, not occlusion/face-identifier failures) doesn't trigger.

Fraud enforcement is explicitly disabled: [3](#0-2) 

`enroll_user::Plan::run` then unconditionally computes the signature whenever a pipeline is present: [4](#0-3) 
`make_signature` reads only `iris_code`/`mask_code`/version fields and calls `secure_element::sign`, never consulting `pipeline.occlusion` or `pipeline.face_identifier_fraud_checks`: [5](#0-4) 

`debug_report::Builder::occlusion_error` and `face_identifier_results` (`src/debug_report.rs:585-598`) exist purely to populate `PipelineErrors` for the debug/telemetry bundle, with no return value or side effect that could halt the signing/enrollment flow: [6](#0-5) 

Thus a session where the occlusion detector or the face-identifier fraud model errors out (e.g., an attacker deliberately occluding the setup to force an `Err` on that specific check while iris codes are still computed by the separate iris agent) still proceeds through `secure_element::sign`, producing a valid signature over iris codes for a session that failed a fraud/occlusion signal. The signature and pipeline are then submitted to the backend via `signup_post::request` (`src/plans/enroll_user.rs:91-102`), so the only remaining gate is backend-side validation, if any — but the Orb-local fail-closed invariant ("signing must not occur over a failed/missing fraud/occlusion signal") is violated locally before that submission.

### Impact Explanation
This weakens Orb-local fail-closed guarantees for iris-code signing. Signing (secure element attestation) is meant to certify Orb-local integrity of the biometric session; here it can be produced even though the local occlusion or face-identifier fraud checks reported errors. Combined with `detect_fraud` being fully stubbed out (`Ok(false)` always, all fraud checks deleted), the Orb performs essentially no local fraud/occlusion enforcement before signing and submitting a signup, shifting 100% of fraud detection to the backend and creating a signature over data that should have been rejected fail-closed at the Orb.

### Likelihood Explanation
Any unprivileged attacker running their own signup session can trigger occlusion or face-identifier pipeline errors (e.g. via unusual eye/face conditions, degenerate input to the occlusion/face-identifier ONNX models) while iris codes are still extracted by the separate iris pipeline stage. No special access is needed — this is reachable purely through the normal Orb signup UX/capture flow already exercised by every attacker-controlled signup.

### Recommendation
In `biometric_pipeline()` (`src/plans/mod.rs`), treat `pipeline.occlusion.is_err()` or `pipeline.face_identifier_fraud_checks.is_err()` as fatal to the pipeline stage (return `Ok(None)` and fail the signup), or explicitly gate `enroll_user`/`make_signature` on both fields being `Ok` before calling `secure_element::sign`. Restore `detect_fraud` to a fail-closed check rather than an unconditional `Ok(false)`.

### Proof of Concept
Integration test plan (to be added near `src/plans/enroll_user.rs` tests or a new integration test):
1. Construct a `biometric_pipeline::Pipeline` with valid `v2.eye_left`/`eye_right` `iris_code`/`mask_code` fields, but set `pipeline.occlusion = Err(...)` and/or `pipeline.face_identifier_fraud_checks = Err(...)`.
2. Call `enroll_user::Plan { pipeline: Some(&pipeline), .. }.run(orb)` (or directly call the private `make_signature`).
3. Assert that no signature is produced (`Status::SignatureCalculationError` or an equivalent fail-closed status) and `secure_element::sign` is never invoked — currently the test would show `make_signature` succeeds and returns `Ok(signature)`, proving the flaw.
4. As a secondary check, assert `Plan::detect_fraud` returns `Ok(true)` (fraud detected) for such a pipeline instead of unconditionally `Ok(false)`.

### Citations

**File:** src/plans/mod.rs (L1355-1359)
```rust
        debug_report.face_identifier_results(pipeline.face_identifier_fraud_checks.clone());
        debug_report.self_custody_bundle(pipeline.face_identifier_bundle.clone().ok());
        debug_report.self_custody_thumbnail(pipeline.face_identifier_bundle.clone().ok());
        debug_report.occlusion_error(pipeline.occlusion.clone().err());
        tracing::info!("Occlusion Detection result: {:?}", pipeline.occlusion);
```

**File:** src/plans/mod.rs (L1386-1388)
```rust
        orb.ui.biometric_pipeline_success();
        Ok(Some(pipeline))
    }
```

**File:** src/plans/mod.rs (L1390-1406)
```rust
    /// Performs the fraud checks.
    #[allow(clippy::too_many_lines)]
    async fn detect_fraud(
        &mut self,
        orb: &mut Orb,
        _debug_report: &mut debug_report::Builder,
        pipeline: Option<&biometric_pipeline::Pipeline>,
    ) -> Result<bool> {
        orb.set_phase("Fraud detection").await;
        let Some(_pipeline) = pipeline else {
            return Ok(false);
        };

        // FOSS: WE HAVE DELETED ALL FRAUD CHECKS

        Ok(false)
    }
```

**File:** src/plans/enroll_user.rs (L74-85)
```rust
        let signature = if let Some(p) = self.pipeline.cloned() {
            match task::spawn_blocking(move || make_signature(&user_qr_code, &p)).await {
                Ok(Ok(signature)) => Some(signature),
                Ok(Err(err)) => {
                    tracing::error!("Failed to calculate signature: {err:?}");
                    return Status::SignatureCalculationError;
                }
                Err(err) => {
                    tracing::error!("Failed to calculate signature: {err:?}");
                    return Status::SignatureCalculationError;
                }
            }
```

**File:** src/plans/enroll_user.rs (L290-304)
```rust
fn make_signature(user_qr_code: &qr_scan::user::Data, pipeline: &Pipeline) -> Result<String> {
    let mut ctx = Context::new(&SHA256);
    ctx.update(ORB_ID.as_str().as_bytes());
    ctx.update(user_qr_code.user_id.as_bytes());
    ctx.update(pipeline.v2.ir_net_version.as_bytes());
    ctx.update(pipeline.v2.iris_version.as_bytes());
    ctx.update(pipeline.v2.eye_left.iris_code.as_bytes());
    ctx.update(pipeline.v2.eye_left.mask_code.as_bytes());
    ctx.update(pipeline.v2.eye_left.iris_code_version.as_bytes());
    ctx.update(pipeline.v2.eye_right.iris_code.as_bytes());
    ctx.update(pipeline.v2.eye_right.mask_code.as_bytes());
    ctx.update(pipeline.v2.eye_right.iris_code_version.as_bytes());
    let signed = secure_element::sign(ctx.finish())?;
    Ok(BASE64.encode(&signed))
}
```

**File:** src/debug_report.rs (L585-598)
```rust
    pub fn face_identifier_results(
        &mut self,
        checks: Result<face_identifier::FraudChecks, PyError>,
    ) -> &mut Self {
        match checks {
            Ok(t) => self.fraud_check_results.face_identifier_checks = Some(t),
            Err(e) => self.pipeline_errors.face_identifier_error = Some(e),
        }
        self
    }

    pub fn occlusion_error(&mut self, error: Option<PyError>) {
        self.pipeline_errors.occlusion_error = error;
    }
```
