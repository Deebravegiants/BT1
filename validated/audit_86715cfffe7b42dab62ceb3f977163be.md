### Title
`debug_report::Builder` signup status setters can be finalized more than once, allowing a fraud verdict to be silently overwritten - (File: `src/debug_report.rs`)

### Summary
`prePO`'s `setFinalLongPayout()` bug class is: a function that finalizes a critical outcome value has no guard against being invoked a second time, so a later call silently overwrites an earlier finalized decision and downstream consumers act on inconsistent state. The same pattern exists in `orb-core`'s `debug_report::Builder`, where the `signup_status` field — which records whether a signup was `Success`, `Fraud`, `OrbFailure`, `ServerFailure`, etc. — is set via several independent setters that all perform an unconditional `self.signup_status = Some(...)` with no check that the field was already finalized.

### Finding Description
`Builder::signup_successful`, `Builder::signup_fraud`, `Builder::signup_orb_failure`, and `Builder::signup_server_failure` all write directly to `self.signup_status` without any guard: [1](#0-0) 

Compare this to the sibling field `enrollment_status`, where the authors were aware that calling a "finalizing" setter twice is a hazard and added a warning (but still no actual guard, and only for that one field): [2](#0-1) 

`signup_status` is the field that ultimately drives the post-signup decision logic. It is consumed in `after_signup`, which reads `debug_report.signup_status` and dispatches to `ui_complete_signup`, which explicitly branches on `SignupStatus::Fraud` vs `SignupStatus::Success` to decide whether to notify the user of a failed (fraud) signup or a successful one: [3](#0-2) 

Because none of `signup_successful()`, `signup_fraud()`, `signup_orb_failure()`, or `signup_server_failure()` check `self.signup_status.is_some()` before overwriting, any code path in the signup pipeline (`src/plans/mod.rs`) that calls one of these setters after an earlier setter already ran will silently discard the previous verdict — exactly analogous to `PrePOMarket.setFinalLongPayout()` being callable a second time and overwriting the first payout finalization without any `require` guard. In the prePO bug, the second write left the market insolvent relative to already-processed redemptions; here, a second write to `signup_status` leaves the on-orb decision object inconsistent with whatever fraud/enrollment logic already ran and can flip the final signup outcome (e.g., a signup that was flagged `Fraud` can be overwritten to `Success`, or vice versa) depending on call order in the master plan.

### Impact Explanation
If any code path calls a `signup_status`-setting method twice — e.g., a fraud/anti-spoof check flags the signup as `Fraud` but a later step in the pipeline (retry, extension flow, or an error-recovery branch) subsequently calls `signup_successful()` (or another status setter) — the final `SignupStatus` persisted into the debug report and used to drive `ui_complete_signup` / backend reporting would reflect the *last* write, not the fraud determination. This is a misattributed-signup-outcome class impact: a signup that was internally detected as fraudulent/liveness-failed could be finalized and reported as `Success`, bypassing the fraud/liveness enforcement that had already run. Conversely a legitimate signup's success indicator could be clobbered into a failure state, causing incorrect denial. Both are direct analogs to the insolvency-via-double-finalization root cause in the referenced report.

### Likelihood Explanation
The likelihood is bounded by whether the current call sites in `src/plans/mod.rs` actually invoke more than one of these setters for the same `debug_report::Builder` instance during a single signup, and in what order (fraud-then-success vs success-then-fraud). I was not able to fully enumerate all 5 call sites in `src/plans/mod.rs` in the time available to confirm a concrete double-invocation trace; the index only confirmed the setter definitions and their unconditional-overwrite implementation, plus one confirmed call sequence in `after_signup`/`ui_complete_signup` that treats `signup_status` as the sole source of truth. The vulnerability class (missing "already finalized" guard on a security-relevant terminal state, exactly as in the source report) is proven at the code level; whether it is reachable today depends on future/edge-case control flow (e.g., extension modes, retries, or added code paths) rather than a single obviously-reachable line, so likelihood should be treated as **moderate** pending full call-graph verification of `src/plans/mod.rs`.

### Recommendation
Add an idempotency guard to every `signup_status`-setting method in `src/debug_report.rs`, mirroring the fix recommended in the original report (`require(finalLongPayout > MAX_PAYOUT)` before allowing a new write). Concretely:
```rust
pub fn signup_fraud(&mut self) -> &mut Self {
    debug_assert!(self.signup_status.is_none(), "signup_status already finalized");
    if self.signup_status.is_none() {
        self.signup_status = Some(SignupStatus::Fraud);
    }
    self
}
```
Apply the same "set-once" invariant to `signup_successful`, `signup_orb_failure`, and `signup_server_failure`, and audit `src/plans/mod.rs` to ensure no code path can legitimately call more than one of these setters for the same signup attempt. Given a fraud/security-relevant verdict should never be downgraded, consider making `Fraud` sticky (i.e., once `Fraud` is set, reject subsequent overwrites entirely) rather than purely first-write-wins.

### Proof of Concept
1. During a signup, an internal fraud/liveness check runs and calls `debug_report.signup_fraud()`, setting `signup_status = Some(SignupStatus::Fraud)`. [4](#0-3) 
2. Later in the same signup's control flow (e.g., an error-recovery, retry, or extension-mode branch in `src/plans/mod.rs`) another setter such as `signup_successful()` is invoked on the same `Builder` instance, unconditionally overwriting the field. [5](#0-4) 
3. `after_signup` reads the now-overwritten `signup_status` and calls `ui_complete_signup`, which — seeing `SignupStatus::Success` instead of `SignupStatus::Fraud` — informs the user/UI/backend of a successful signup rather than surfacing the fraud rejection that had already been determined. [6](#0-5)

### Citations

**File:** src/debug_report.rs (L489-508)
```rust
    pub fn signup_successful(&mut self) -> &mut Self {
        self.signup_status = Some(SignupStatus::Success);
        self
    }

    pub fn signup_fraud(&mut self) -> &mut Self {
        self.signup_status = Some(SignupStatus::Fraud);
        self
    }

    pub fn signup_orb_failure(&mut self) -> &mut Self {
        self.signup_status = Some(SignupStatus::OrbFailure);
        self
    }

    pub fn signup_server_failure(&mut self) -> &mut Self {
        self.signup_status = Some(SignupStatus::ServerFailure);
        self.failure_feedback_after_capture.push(AfterCaptureFeedbackMessage::ServerError);
        self
    }
```

**File:** src/debug_report.rs (L510-526)
```rust
    pub fn signup_orb_relay_failure(&mut self) -> &mut Self {
        self.signup_status = Some(SignupStatus::OrbRelayFailure);
        if self.enrollment_status.is_some() {
            tracing::error!("Don't use this call after enrollment_status registration");
        }
        self.enrollment_status = Some(enroll_user::Status::Error);
        self
    }

    pub fn signup_app_incompatible_failure(&mut self) -> &mut Self {
        self.signup_status = Some(SignupStatus::AppIncompatible);
        if self.enrollment_status.is_some() {
            tracing::error!("Don't use this call after enrollment_status registration");
        }
        self.enrollment_status = Some(enroll_user::Status::Error);
        self
    }
```

**File:** src/plans/mod.rs (L1475-1510)
```rust
        let signup_status = debug_report.signup_status.clone();

        let enrollment_status = debug_report.enrollment_status.clone();
        let failure_feedback = debug_report.failure_feedback_after_capture_proto();
        Box::pin(self.upload_debug_report(orb, debug_report)).await?;

        if let Some(signup_status) = signup_status {
            Self::ui_complete_signup(orb, &signup_status, enrollment_status);
        }

        if orb.config.lock().await.self_serve {
            if let Some(relay) = orb.orb_relay.as_mut() {
                relay
                    .send(self_serve::orb::v1::SignupEnded {
                        success: signup_result.success,
                        failure_feedback,
                    })
                    .await
                    .inspect_err(|e| tracing::error!("Relay: Failed to SignupEnded: {e}"))?;
            }
        }

        Ok(())
    }

    fn ui_complete_signup(
        orb: &mut Orb,
        signup_status: &debug_report::SignupStatus,
        enrollment_status: Option<enroll_user::Status>,
    ) {
        match signup_status {
            SignupStatus::Success => orb.ui.signup_success(),
            SignupStatus::OrbFailure | SignupStatus::InternalError => {
                notify_failed_signup(orb, Some(SignupFailReason::Unknown));
            }
            SignupStatus::Fraud => notify_failed_signup(orb, Some(SignupFailReason::Verification)),
```
