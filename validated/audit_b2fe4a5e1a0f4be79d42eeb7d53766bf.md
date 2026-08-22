### Title
Fraud detection unconditionally returns "no fraud" regardless of biometric pipeline data - (File: `src/plans/mod.rs`)

### Summary
The Sherlock finding describes `XChainController.pushVaultAmounts()` calling `xProvider.getDecimals()`, which always resolves against a fixed context (MainNet) instead of the actual per-call context, silently producing a wrong result that is then trusted for a security-critical calculation (the exchange rate), breaking the entire downstream logic. The equivalent bug class — a security-critical decision function that always returns a fixed, context-independent result instead of evaluating the actual input it receives — exists in `MasterPlan::detect_fraud`.

### Finding Description
`detect_fraud` is the function in the signup pipeline responsible for evaluating whether a completed biometric capture/pipeline should be flagged as fraudulent before enrollment proceeds: [1](#0-0) 

Regardless of the contents of `pipeline` (the actual per-signup biometric pipeline data passed in), the function takes a reference to it (`_pipeline`, explicitly unused) and unconditionally returns `Ok(false)` — i.e., "not fraud" — for every signup that reaches this point. This mirrors the `getDecimals()` bug class: the function signature suggests it evaluates the specific context/input given (the current signup's pipeline), but the implementation always resolves to a fixed, input-independent outcome ("no fraud"), just as `getDecimals()` always resolved against the fixed MainNet context regardless of the actual vault chain.

The result of `detect_fraud` feeds directly into the signup reason logic used to gate enrollment: [2](#0-1) [3](#0-2) 

Since `detect_fraud` always returns `false`, `signup_reason` can never be set to `SignupReason::Fraud` through this path, and `report_signup_reason`/`debug_report.signup_fraud()` are effectively dead code for on-device fraud enforcement.

### Impact Explanation
This breaks the on-device fraud/liveness enforcement gate described by `SignupReason::Fraud` ("Signup was detected as a fraud attempt at the orb"): [4](#0-3) 

Any local (orb-side) fraud detection intended to stop enrollment or tag the signup as fraudulent before biometric data leaves the device is a no-op. All signups proceed as if no fraud condition was ever detected at the orb, relying entirely on backend-side checks (as the enum doc comment itself notes: "not to be confused with the backend fraud checks"). This directly matches the accepted impact categories (fraud/liveness bypass).

### Likelihood Explanation
The bypass is deterministic and always reachable whenever a pipeline is present — there is no conditional branch, feature flag check, or data-dependent logic that could ever cause it to return `true`: [5](#0-4) 

This is explicitly called out in the code comment ("FOSS: WE HAVE DELETED ALL FRAUD CHECKS"), confirming the checks were removed for this build variant rather than being conditionally disabled, meaning the bypass is guaranteed on every signup that reaches `detect_fraud` in this codebase, not merely a rare edge case.

### Recommendation
If on-device fraud detection is required for this build, `detect_fraud` should actually evaluate `pipeline` (the same way `getDecimals()` should have resolved the vault's actual chain rather than a fixed one) instead of ignoring it and returning a hardcoded `false`. At minimum, callers relying on `detect_fraud`'s result to set `SignupReason::Fraud` should not assume local fraud enforcement is active, and any compliance/security documentation should clearly state that fraud enforcement for this build is backend-only.

### Proof of Concept
1. Run any signup where `pipeline` is `Some(...)` (i.e., biometric pipeline data was captured), regardless of its contents.
2. `detect_fraud` is invoked with that `pipeline`: [6](#0-5) 
3. Execution unconditionally falls through to `Ok(false)` — no fraud is ever flagged, and `signup_reason` remains `Normal`/whatever was passed in, never transitioning to `Fraud` via this function, regardless of the actual pipeline content.

### Citations

**File:** src/plans/mod.rs (L639-663)
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
    }
```

**File:** src/plans/mod.rs (L665-683)
```rust
    fn report_signup_reason(
        success: bool,
        signup_reason: SignupReason,
        debug_report: &mut debug_report::Builder,
    ) {
        if signup_reason == SignupReason::Failure {
            tracing::info!("User enrollment failed due to a failure in the pipeline");
            debug_report.signup_orb_failure();
        } else if signup_reason == SignupReason::Fraud {
            tracing::info!("User enrollment failed due to fraud");
            debug_report.signup_fraud();
        } else if success {
            debug_report.signup_successful();
            dd_incr!("main.count.signup.result.success.successful_signup");
        } else {
            tracing::info!("User enrollment failed");
            debug_report.signup_server_failure();
        }
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

**File:** src/backend/signup_post.rs (L72-82)
```rust
/// Every signup needs to be tagged with a reason for the backend to process it.
#[derive(Serialize, Debug, Default, Copy, Clone, PartialEq, Eq)]
pub enum SignupReason {
    /// Signup was successfully processed on the Orb.
    #[default]
    Normal,
    /// Signup failed due to some agent dying in the biometric pipeline or some internal error.
    Failure,
    /// Signup was detected as a fraud attempt at the orb (not to be confused with the backend fraud checks).
    Fraud,
}
```
