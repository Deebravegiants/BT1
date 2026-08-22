### Title
Fraud-detection stage in the signup pipeline is a permanent no-op, allowing any signup (including fraudulent/duplicate ones) to be committed as legitimate - (File: `src/plans/mod.rs`, `src/plans/fraud_check.rs`)

### Summary
The reported DeFi bug's root cause is a security gate (`_is_liquidatable`) that is checked at the wrong point in the flow and never re-validated after an attacker-controlled step, so an invalid state gets permanently committed. The orb-core signup pipeline has the structurally analogous defect in `detect_fraud`: the gate exists syntactically in `do_signup`, but it is hard-coded to never trigger, so the "commit" step (marking the signup as `SignupReason::Normal` and proceeding to enrollment/PCP upload) always happens regardless of the actual fraud signal.

### Finding Description
In `MasterPlan::do_signup`, the signup outcome is derived from `detect_fraud`: [1](#0-0) 

`detect_fraud` is supposed to be the check that gates whether a signup is flagged as fraudulent before the identity commitment/enrollment step proceeds: [2](#0-1) 

However `N_FRAUD_CHECKS` is hard-coded to `0` and the `Report` struct backing this pipeline carries no checks at all: [3](#0-2) [4](#0-3) 

As a result, `detect_fraud` unconditionally returns `Ok(false)` for any completed biometric pipeline, so `fraud_detected` is always `false` and `signup_reason` is always `SignupReason::Normal` whenever the pipeline itself succeeds - independent of any actual fraud signal that a real fraud engine would have produced. This is the same shape of bug as the sandwich-attack finding: a checkpoint that is supposed to gate an irreversible state transition (there, opening/closing a leveraged position; here, committing a signup/identity binding) is nominally present in the control flow but structurally cannot block the transition, because the check itself never evaluates real data.

Downstream of this bypass, `signup_reason` feeds directly into `build_pcp` (personal custody package creation) and into the `user_centric_signup` success determination: [5](#0-4) [6](#0-5) 

Both paths treat `SignupReason::Normal` as authoritative proof of a clean, non-fraudulent signup and proceed to upload/commit biometric tiers and enrollment status.

### Impact Explanation
Since fraud detection can never fire, any completed biometric capture is treated as fraud-free and eligible for identity commitment, enrollment, and PCP upload - even in cases (duplicate/Sybil signups, spoofing, multiple faces, underage users flagged by other signals, etc.) that a functioning fraud engine would have flagged. This is a concrete fraud/liveness-enforcement bypass reachable by any unprivileged user attempting a signup, and it can lead to misattributed or duplicate signups being accepted as legitimate, and to biometric data being disclosed/committed for signups that should have been rejected.

### Likelihood Explanation
This is deterministically reachable on every signup that completes the biometric pipeline - `detect_fraud` always returns `false`, so there is no probabilistic or race-condition element; the bypass is unconditional for the given code path (not a per-request timing race like the DeFi sandwich, but a structurally permanent gate failure with equivalent effect).

### Recommendation
Wire `detect_fraud`/`fraud_check::Report`/`Pipeline` back to real fraud signals (occlusion, duplicate detection, face-identifier fraud checks, multiple faces, underage detection, etc.) so that `N_FRAUD_CHECKS` and `fraud_checks()` reflect actual pipeline outputs, and ensure `signup_reason` cannot become `SignupReason::Normal` unless those checks genuinely ran and passed. Add a fail-closed default consistent with `fraud_checks_strict`'s stated intent ("if fraud data are missing, we assume fraud is detected") rather than a hard-coded `Ok(false)`.

### Proof of Concept
1. Any user completes biometric capture such that `biometric_pipeline` returns `Some(pipeline)` (this only requires a normal, successful capture - no special crafted input needed).
2. `detect_fraud` is called with this pipeline; because `N_FRAUD_CHECKS == 0` and no checks are defined, it unconditionally returns `Ok(false)`. [7](#0-6) 
3. `fraud_detected` is `false`, so `signup_reason` is computed as `SignupReason::Normal`. [8](#0-7) 
4. The signup proceeds to `build_pcp`, PCP tier upload, and enrollment/success determination as if no fraud engine issue could ever exist, regardless of the true fraud state of the signup.

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

**File:** src/plans/mod.rs (L572-598)
```rust
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
```

**File:** src/plans/mod.rs (L639-662)
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

        Self::report_signup_reason(success, signup_reason, debug_report);

        result.success =
            debug_report.enrollment_status.as_ref().map_or(false, enroll_user::Status::is_success);
        Ok(result)
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

**File:** src/plans/fraud_check.rs (L10-21)
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
```

**File:** src/plans/fraud_check.rs (L64-74)
```rust
impl Report {
    const DATADOG_TAGS: [&'static str; N_FRAUD_CHECKS] = [];

    fn fraud_checks(&self) -> [Option<bool>; N_FRAUD_CHECKS] {
        []
    }

    /// If fraud data are missing, we assume fraud is detected.
    fn fraud_checks_strict(&self) -> [bool; N_FRAUD_CHECKS] {
        self.fraud_checks().map(|v| v.unwrap_or(true))
    }
```
