Based on the investigation, the strongest reachable analog to the "missing slippage/output validation" bug class is not a numeric-threshold gap but a completely stubbed-out validation gate: the fraud-detection check in the signup pipeline is a no-op that always reports "no fraud," structurally identical to a swap path that never validates its output before committing state.

### Title
Fraud Detection Pipeline Always Reports No Fraud, Bypassing Duplicate/Fraud Validation Before Signup Commitment - (File: src/plans/mod.rs)

### Summary
The `MasterPlan::detect_fraud` function, which is supposed to gate signup finalization on the result of fraud/liveness checks, unconditionally returns `Ok(false)` regardless of the biometric pipeline output, meaning no signup is ever blocked or flagged for fraud through this path.

### Finding Description
Just as `SpotManager::buy()`/`sell()` in the reference report accept a swap result (`amountOut`) without validating it against any minimum acceptable bound before committing state (`spotBuyCallback`/`spotSellCallback`), `MasterPlan::do_signup` accepts the result of `detect_fraud` without any actual validation logic behind it, and then unconditionally proceeds to build and upload the Personal Custody Package (PCP) and enroll the user.

`detect_fraud` is implemented as:
```rust
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
``` [1](#0-0) 

This feeds directly into the decision on how to classify and process the signup:
```rust
let fraud_detected = !self.skip_fraud_checks()
    && self.detect_fraud(orb, debug_report, pipeline.as_ref()).await?;
let signup_reason = if pipeline.is_none() {
    SignupReason::Failure
} else if fraud_detected {
    SignupReason::Fraud
} else {
    SignupReason::Normal
};
``` [2](#0-1) 

The underlying `fraud_check::Report` and `BackendConfig` types are also emptied out (`N_FRAUD_CHECKS = 0`), confirming there is no check logic left to invoke:
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
...
pub struct BackendConfig {}
...
pub struct Report {}
``` [3](#0-2) 

Regardless of what the biometric pipeline (iris codes, face identifier, occlusion) actually produces, `signup_reason` can never become `SignupReason::Fraud` through this code path — every signup that completes biometric capture and the pipeline is unconditionally treated as `SignupReason::Normal` and proceeds to PCP construction, upload, and enrollment.

### Impact Explanation
Because the fraud-detection "output validation" step is a hard-coded no-op, any signup that reaches the pipeline stage will always be classified and enrolled as a legitimate/normal signup, with no gate to catch duplicate signups or fraud-indicating biometric conditions detected by the underlying models. This is structurally the same failure mode as the reported issue: a critical check on a computed result is missing, so downstream state-changing actions (`spotBuyCallback`/`enroll_user`) execute unconditionally on unvalidated results, enabling misattributed/fraudulent enrollment to be accepted as legitimate.

### Likelihood Explanation
This code path is reachable by any unprivileged user completing a normal signup flow — no operator/hardware/malicious-peer access is required. Every signup that isn't a pipeline failure automatically takes the `SignupReason::Normal` branch since `fraud_detected` can never be `true`, so the likelihood of hitting the affected code is effectively 100% for every processed signup.

### Recommendation
Restore fraud-check evaluation logic in `detect_fraud` (or wire in the actual fraud engine) so that `fraud_detected` reflects the real output of `biometric_pipeline::Pipeline` (e.g., occlusion, contact lens, multi-face, underage, and other checks defined in `PipelineFailureFeedbackMessage`), and ensure `SignupReason::Fraud` is reachable and enforced before PCP build/upload/enrollment proceeds.

### Proof of Concept
1. Complete a normal signup through biometric capture and the biometric pipeline.
2. Regardless of the pipeline output (`pipeline.as_ref()` in `detect_fraud`), observe that `detect_fraud` always returns `Ok(false)`. [1](#0-0) 
3. `signup_reason` is computed as `SignupReason::Normal` for every non-failure pipeline result. [4](#0-3) 
4. The flow proceeds directly to `build_pcp`, PCP tier uploads, and `enroll_user`, with no fraud-based blocking possible. [5](#0-4)

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

**File:** src/plans/mod.rs (L580-636)
```rust
            let packages = match Box::pin(self.build_pcp(
                orb,
                credentials,
                &capture,
                pipeline.as_ref(),
                debug_report,
                signup_reason,
            ))
            .await
            {
                Ok(Some(p)) => p,
                Ok(None) => {
                    return Ok(result);
                }
                Err(e) => {
                    tracing::error!("{e}");
                    return Ok(result);
                }
            };
            data_uploader::wait_queues(orb.data_uploader.enabled().unwrap()).await?;
            if !self
                .upload_pcp_tier_0(
                    orb,
                    &result.signup_id,
                    &user_id,
                    packages.tier0,
                    packages.tier0_checksum,
                    if pcp_version >= 3 { Some(0) } else { None },
                )
                .await?
            {
                return Ok(result);
            }
            if pcp_version >= 3 {
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id: user_id.clone(),
                        data: packages.tier1,
                        checksum: packages.tier1_checksum.as_ref().to_vec(),
                        tier: 1,
                    })))
                    .await?;
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id,
                        data: packages.tier2,
                        checksum: packages.tier2_checksum.as_ref().to_vec(),
                        tier: 2,
                    })))
                    .await?;
            }
```

**File:** src/plans/mod.rs (L1392-1406)
```rust
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

**File:** src/plans/fraud_check.rs (L10-36)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;

/// Convenience wrapper struct for the Fraud Check Engine's configuration coming from the backend.
#[cfg_attr(test, derive(Default))]
#[derive(
    Archive, Serialize, Deserialize, SerdeDeserialize, SerdeSerialize, Debug, Clone, JsonSchema,
)]
#[serde(rename_all = "PascalCase")]
#[allow(clippy::struct_excessive_bools)]
pub struct BackendConfig {}

// Helper function to deserialize a Duration from a u64 representing milliseconds
#[allow(dead_code)]
fn deserialize_duration_from_millis<'de, D>(deserializer: D) -> Result<Duration, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let millis = <u64 as SerdeDeserialize>::deserialize(deserializer)?;
    Ok(Duration::from_millis(millis))
}

/// The results of the fraud checks.
#[allow(clippy::struct_excessive_bools)]
#[derive(Debug, Default, SerdeSerialize, JsonSchema, Clone)]
pub struct Report {}
```
