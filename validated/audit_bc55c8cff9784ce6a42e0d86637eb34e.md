### Title
Secure-element signature generation ignores fraud/occlusion verdict, allowing valid attestation over fraudulent iris capture - (File: src/plans/enroll_user.rs)

### Summary
`enroll_user::Plan::run` computes and signs the iris-code commitment via `make_signature`/`secure_element::sign` solely based on `Pipeline` being `Some`, with no check of `pipeline.occlusion`, `pipeline.face_identifier_fraud_checks`, or the computed `signup_reason` (Normal/Fraud/Failure). The signature is generated and sent to the backend before/independently of any fail-closed liveness or fraud verdict.

### Finding Description
In `src/plans/mod.rs`, `do_signup` runs the pipeline and fraud detection, computing `signup_reason` from `fraud_detected`: [1](#0-0) 
It then unconditionally proceeds to `enroll_user`, passing `pipeline.as_ref()` and `signup_reason` without ever skipping signature generation when `signup_reason == SignupReason::Fraud`: [2](#0-1) 

In `enroll_user::Plan::run`, whenever `self.pipeline` is `Some`, `make_signature` is called and, on success, the signature is always attached to the `signup_post::request` regardless of `self.signup_reason`: [3](#0-2) 

`make_signature` itself hashes only `user_id`, `ir_net_version`, `iris_version`, and the iris/mask codes for both eyes, and calls `secure_element::sign` directly — it never reads `pipeline.occlusion` or `pipeline.face_identifier_fraud_checks`: [4](#0-3) 

Additionally, in this build, `detect_fraud` — the only gate that could set `signup_reason` to `Fraud` — has had all real fraud checks removed and unconditionally returns `Ok(false)` whenever a pipeline exists: [5](#0-4) 

The biometric pipeline building code shows that `occlusion` and `face_identifier_fraud_checks` are legitimate per-signup verdict fields (`Ok`/`Err`) attached to `Pipeline`, recorded into the debug report but never consulted before generating the signature: [6](#0-5) 

As a result, any code path that yields `Pipeline = Some(...)` — regardless of `occlusion` being `Err`, `face_identifier_fraud_checks` being `Err`, or (in an upstream build with real fraud checks restored) `fraud_detected == true` — still causes a cryptographically valid secure-element signature to be computed over that session's iris/mask codes and sent to the backend via `signup_post::request`. The signature itself carries no information about the fraud/occlusion/liveness verdict; that information is only conveyed via the separate, client-controlled `reason` form field (`NORMAL`/`FRAUD`/`FAILURE`), which is not bound into the signed data and is decided entirely by orb-core logic that (in this build) never returns true.

### Impact Explanation
This breaks the intended attestation invariant that a secure-element signature should reflect a fail-closed liveness/fraud verdict, not merely "a pipeline object exists." The signature is the cryptographic device attestation binding `user_id || ir_net_version || iris_version || iris_code || mask_code`; if it is issued even for occluded/fraud-flagged/spoofed captures, the backend receives a validly signed iris-code commitment for data that should have been rejected on-device. This corresponds to a liveness/fraud-bypass and attestation-forgery-class impact: a fraudulent/spoofed capture that completes the pipeline can still get an authentic-looking signed commitment sent upstream, undermining any backend trust placed in the on-orb fraud gate.

### Likelihood Explanation
Preconditions are exactly as stated: the pipeline must complete (`Pipeline = Some`), independent of the fraud/occlusion verdict. This is fully reachable from an attacker's own signup session (no privileged access needed) by presenting a capture that passes the biometric pipeline's minimum requirements to produce iris/mask codes but fails occlusion or face-identifier fraud checks. In the current FOSS build, this is deterministic since `detect_fraud` always returns `false`, so signing happens on every pipeline success unconditionally.

### Recommendation
Gate `make_signature`/`secure_element::sign` (or the call to `enroll_user` from `do_signup`) on the fraud/occlusion verdict: only compute and send a signature when `signup_reason == SignupReason::Normal` and `pipeline.occlusion.is_ok()` and `pipeline.face_identifier_fraud_checks.is_ok()` (or an equivalent restored, non-deleted fraud check). Consider also binding the fraud/liveness verdict into the signed payload itself so the backend can cryptographically verify the reason was not tampered with in transit.

### Proof of Concept
Unit test in `src/plans/enroll_user.rs` (or a new test module):
1. Construct a `Pipeline` with `occlusion = Err(...)` and/or `face_identifier_fraud_checks = Err(...)`, but valid `v2.eye_left`/`v2.eye_right` iris/mask codes.
2. Call `make_signature(&user_qr_code, &pipeline)` directly.
3. Assert the call returns `Ok(signature)` (a valid base64 signature), proving no fraud/occlusion gate exists before `secure_element::sign` is invoked.
4. Additionally, in a `do_signup`-level integration test, mock `detect_fraud` to return `true` (simulating fraud detection) and confirm `enroll_user` is still invoked with `pipeline.as_ref()` producing a valid signature sent via `signup_post::request`, with only the `reason` field differing (`FRAUD` vs `NORMAL`), demonstrating the signature is issued for fraudulent sessions.

### Citations

**File:** src/plans/mod.rs (L562-571)
```rust
        let pipeline = Box::pin(self.biometric_pipeline(orb, debug_report, &capture)).await?;
        let fraud_detected = !self.skip_fraud_checks()
            && self.detect_fraud(orb, debug_report, pipeline.as_ref()).await?;
        let signup_reason = if pipeline.is_none() {
            SignupReason::Failure
        } else if fraud_detected {
            SignupReason::Fraud
        } else {
            SignupReason::Normal
        };
```

**File:** src/plans/mod.rs (L639-656)
```rust
        let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
        {
            debug_report.enrollment_status(match signup_reason {
                SignupReason::Normal => enroll_user::Status::Success,
                _ => enroll_user::Status::Error,
            });
            signup_reason == SignupReason::Normal
        } else {
            Box::pin(self.enroll_user(
                orb,
                debug_report,
                &capture,
                pipeline.as_ref(),
                signup_reason,
            ))
            .await
            .is_success()
        };
```

**File:** src/plans/mod.rs (L1343-1359)
```rust
        debug_report.iris_model_metadata(
            pipeline.v2.eye_left.metadata.clone(),
            pipeline.v2.eye_right.metadata.clone(),
        );
        debug_report.iris_normalized_images(
            pipeline.v2.eye_left.iris_normalized_image.clone(),
            pipeline.v2.eye_right.iris_normalized_image.clone(),
            pipeline.v2.eye_left.iris_normalized_image_resized.clone(),
            pipeline.v2.eye_right.iris_normalized_image_resized.clone(),
        );
        debug_report.mega_agent_one_config(pipeline.mega_agent_one_config.clone());
        debug_report.mega_agent_two_config(pipeline.mega_agent_two_config.clone());
        debug_report.face_identifier_results(pipeline.face_identifier_fraud_checks.clone());
        debug_report.self_custody_bundle(pipeline.face_identifier_bundle.clone().ok());
        debug_report.self_custody_thumbnail(pipeline.face_identifier_bundle.clone().ok());
        debug_report.occlusion_error(pipeline.occlusion.clone().err());
        tracing::info!("Occlusion Detection result: {:?}", pipeline.occlusion);
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

**File:** src/plans/enroll_user.rs (L74-101)
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
        } else {
            None
        };
        tracing::info!("Iris code signature: {:?}", signature);
        let signup_id = self.signup_id.to_string();
        for i in 0..RETRIES_COUNT {
            let response = signup_post::request(
                signature.as_ref(),
                &signup_id,
                &self.operator_qr_code,
                &self.user_qr_code,
                &self.s3_region_str,
                self.capture,
                self.pipeline,
                self.signup_reason,
            )
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
