### Title
`build_pcp` uploads self-custody biometric package without checking the occlusion verdict, allowing occluded/degraded captures to be signed up as genuine - (File: src/plans/mod.rs)

### Finding Description
`MasterPlan::build_pcp` gates the personal custody package build purely on presence checks (`Option`/`Result::ok()` patterns) over `face_identifier_bundle`, its `thumbnail`, `embeddings`, `inference_backend`, and the four normalized iris images [1](#0-0) . It never inspects `pipeline.occlusion`, which is a separate `Result<occlusion::EstimateOutput, PyError>` field on `biometric_pipeline::Pipeline` produced by the occlusion-detection agent [2](#0-1) , and which carries boolean occlusion/eye-glasses/face-mask verdicts and probabilities [3](#0-2) .

Tracing the call chain confirms this: `MasterPlan::biometric_pipeline` (src/plans/mod.rs:1290-1388) only forwards `pipeline.occlusion.clone().err()` to `debug_report.occlusion_error` for logging/telemetry purposes and never fails the pipeline based on a successful-but-"occluded" verdict [4](#0-3) . The result is then passed to `detect_fraud` and independently to `build_pcp` [5](#0-4) . Neither the enforcement inside `build_pcp` nor the earlier `biometric_pipeline` step examines the `occlusion` boolean, `eye_glasses_occlusion`, or `face_mask_occlusion` fields of a *successful* `EstimateOutput`. Only a Python-level exception (`Err(PyError)`) is surfaced, and only as telemetry, not as a gate.

Separately, the `EyesOcclusion` check performed during `biometric_capture` (src/plans/biometric_capture/mod.rs:719-721) only tests whether IR eye frames are entirely missing (`self.left_ir.is_none() || self.right_ir.is_none()`), which is a presence check unrelated to the RGB-based occlusion-detection model's actual occlusion score. It does not substitute for verifying the occlusion agent's verdict.

### Impact Explanation
An occluded-eye or masked-face capture (e.g., partial obstruction that still yields non-null IR/iris frames and a non-error `face_identifier_bundle`) can pass through `build_pcp`, be packaged via `personal_custody_package::Plan::run`, and get uploaded via `upload_personal_custody_package::request` as a fully "successful" signup, despite the occlusion model flagging degraded signal quality. This corresponds to a degraded-signal/fraud-bypass class impact: biometric data of insufficient quality is bound to an identity and uploaded as genuine, undermining the fail-closed guarantee that the occlusion check is supposed to enforce before custody-package creation.

### Likelihood Explanation
The precondition is straightforward and reachable by an unprivileged attacker during their own signup session: present eyes/face in a way that still yields valid IR/iris/face-identifier outputs (non-error) but triggers a positive occlusion/eye-glasses/mask verdict from the RGB occlusion model (e.g., wearing glasses with partial glare, a thin mask, or partial obstruction that the occlusion classifier flags but that doesn't otherwise break IR capture). No privileged access, key leakage, or hardware tampering is required — only control over the presented scene to the camera, consistent with the allowed threat model.

### Recommendation
In `build_pcp` (or earlier in `MasterPlan::biometric_pipeline`/`detect_fraud`), explicitly check `pipeline.occlusion` for both the `Err` case and the positive verdict fields (`occlusion`, `eye_glasses_occlusion`, `face_mask_occlusion`) against the fraud/quality policy, and fail closed (`return Ok(None)` with an appropriate `data_error!`/fraud classification) when occlusion is detected, before proceeding to package and upload biometric data.

### Proof of Concept
Add a unit test in `src/plans/mod.rs` (or a test harness constructing `biometric_pipeline::Pipeline`) that:
1. Constructs a `Pipeline` with `occlusion: Ok(EstimateOutput { occlusion: true, eye_glasses_occlusion: true, face_mask_occlusion: false, .. })` while `face_identifier_bundle` and iris fields are all valid `Some`/`Ok`.
2. Calls `MasterPlan::build_pcp(...)` with this pipeline.
3. Assert the current behavior returns `Ok(Some(PersonalCustodyPackages { .. }))` (demonstrating the bypass), then assert the fix should instead return `Ok(None)` when `occlusion == true`. [6](#0-5) [2](#0-1) [7](#0-6)

### Citations

**File:** src/plans/mod.rs (L562-587)
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
        let user_id = qr_codes.user_qr_code.user_id.clone();
        let user_centric_signup = qr_codes.user_data.user_centric_signup;
        if let Ok(mut credentials) = qr_codes.try_into() {
            let personal_custody_package::Credentials { pcp_version, .. } = &mut credentials;
            if !pcp_v3 {
                *pcp_version = 2;
            }
            let pcp_version = *pcp_version;
            let packages = match Box::pin(self.build_pcp(
                orb,
                credentials,
                &capture,
                pipeline.as_ref(),
                debug_report,
                signup_reason,
            ))
```

**File:** src/plans/mod.rs (L1355-1359)
```rust
        debug_report.face_identifier_results(pipeline.face_identifier_fraud_checks.clone());
        debug_report.self_custody_bundle(pipeline.face_identifier_bundle.clone().ok());
        debug_report.self_custody_thumbnail(pipeline.face_identifier_bundle.clone().ok());
        debug_report.occlusion_error(pipeline.occlusion.clone().err());
        tracing::info!("Occlusion Detection result: {:?}", pipeline.occlusion);
```

**File:** src/plans/mod.rs (L1668-1712)
```rust
        let Some(face_identifier_bundle) =
            pipeline.as_ref().and_then(|p| p.face_identifier_bundle.as_ref().ok())
        else {
            data_error!("face_identifier_bundle");
        };
        if let Some(error) = &face_identifier_bundle.error {
            data_error!(
                "Face identifier bundle contains an error: {error:?}",
                "type:face_identifier_bundle_error"
            );
        }
        let Some(face_identifier_thumbnail) = &face_identifier_bundle.thumbnail else {
            data_error!("face_identifier_bundle.thumbnail");
        };
        let Some(face_identifier_thumbnail_image) = &face_identifier_thumbnail.image else {
            data_error!("face_identifier_bundle.thumbnail.image");
        };
        let Some(face_identifier_embeddings) = &face_identifier_bundle.embeddings else {
            data_error!("face_identifier_bundle.embeddings");
        };
        let Some(face_identifier_inference_backend) = &face_identifier_bundle.inference_backend
        else {
            data_error!("face_identifier_bundle.inference_backend");
        };
        let Some(left_normalized_iris_image) =
            pipeline.as_ref().and_then(|p| p.v2.eye_left.iris_normalized_image.as_ref())
        else {
            data_error!("v2.eye_left.iris_normalized_image");
        };
        let Some(right_normalized_iris_image) =
            pipeline.as_ref().and_then(|p| p.v2.eye_right.iris_normalized_image.as_ref())
        else {
            data_error!("v2.eye_right.iris_normalized_image");
        };
        let Some(left_normalized_iris_image_resized) =
            pipeline.as_ref().and_then(|p| p.v2.eye_left.iris_normalized_image_resized.as_ref())
        else {
            data_error!("v2.eye_left.iris_normalized_image_resized");
        };
        let Some(right_normalized_iris_image_resized) =
            pipeline.as_ref().and_then(|p| p.v2.eye_right.iris_normalized_image_resized.as_ref())
        else {
            data_error!("v2.eye_right.iris_normalized_image_resized");
        };

```

**File:** src/plans/biometric_pipeline/mod.rs (L56-64)
```rust
/// Biometric pipeline output.
#[derive(Clone, Debug)]
pub struct Pipeline {
    /// Pipeline v2 output.
    pub v2: PipelineV2,
    /// Occlusion detection estimate output.
    pub occlusion: Result<occlusion::EstimateOutput, PyError>,
    /// Face identifier model output for the fraud checks.
    pub face_identifier_fraud_checks: Result<face_identifier::FraudChecks, PyError>,
```

**File:** src/agents/python/occlusion.rs (L59-74)
```rust
/// Occlusion detection estimate output.
#[derive(Archive, Clone, Debug, Default, Deserialize, Serialize)]
pub struct EstimateOutput {
    /// Occlusion assert.
    pub occlusion: bool,
    /// Eye glasses probability score.
    pub eye_glasses_probability: f64,
    /// Eye glasses occlusion
    pub eye_glasses_occlusion: bool,
    /// Face mask probability score.
    pub face_mask_probability: f64,
    /// Face mask occlusion
    pub face_mask_occlusion: bool,
    /// Face bounding box.
    pub bbox: Rectangle,
}
```
