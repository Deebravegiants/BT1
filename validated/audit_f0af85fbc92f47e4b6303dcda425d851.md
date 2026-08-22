### Title
User-centric signups skip authoritative backend enrollment verification, allowing local-only signup success determination - (File: `src/plans/mod.rs`)

### Summary
The external report describes a case where `triggerEndEpoch()` treats an oracle price read as though it were essential-path logic, and when that call reverts (Arbitrum sequencer down / grace period), a state transition that should legitimately complete (winners withdrawing) is permanently blocked. The generalizable bug class is: **a step that is supposed to authoritatively confirm/attest a critical state transition is bypassed or short-circuited based on an unreliable/local signal, instead of the authoritative check being consistently enforced.** In orb-core, the analog is in `MasterPlan::do_signup`, where for "user-centric" signups the code entirely skips the backend's authoritative `enroll_user` call (which performs `signup_post`/`signup_poll` — the backend step that detects duplicates, in-flight matches, and backend-side fraud) and instead derives signup success purely from a local, config-dependent `signup_reason` value.

### Finding Description
In `src/plans/mod.rs`, `do_signup` decides whether to call the backend enrollment endpoint based on the `user_centric_signup` flag from `qr_codes.user_data`: [1](#0-0) 

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
        orb, debug_report, &capture, pipeline.as_ref(), signup_reason,
    ))
    .await
    .is_success()
};
```

When `user_centric_signup` is true, `enroll_user::Plan::run` (which POSTs to `/api/v2/signups/{id}` and polls `/api/v1/signups/{id}` until the backend reports `Completed`/`success`) is **never invoked**. The comments in `enroll_user.rs` make clear what that backend round-trip is responsible for catching: [2](#0-1) 

```rust
// This includes the following cases:
//   1. Backend duplicates
//   2. Backend legacy signup requests
//   3. Backend inflight matches
//   4. Backend detected fraud
//   5. Orb agent, internal, capture or pipeline failures
//   6. Orb detected fraud
```

Instead, success is computed purely from `signup_reason`, which is derived on-device from `detect_fraud`: [3](#0-2) 

```rust
async fn detect_fraud(...) -> Result<bool> {
    orb.set_phase("Fraud detection").await;
    let Some(_pipeline) = pipeline else {
        return Ok(false);
    };
    // FOSS: WE HAVE DELETED ALL FRAUD CHECKS
    Ok(false)
}
```

Consequently, for the `user_centric_signup` path, a signup is marked `Success` and the enrollment recorded as valid entirely on-device, without ever consulting the authoritative backend check that is designed to detect duplicate/misattributed enrollments (same iris/person enrolling under a different identity or in-flight against another signup) or backend-side fraud signals. This is structurally the same category of defect as the C4 finding: a step whose completion is required to correctly attribute/finalize a critical action is treated as skippable/local-only, so the system reaches a "success" state without the authoritative verification actually running — as opposed to the C4 case where the authoritative call reverting *blocked* a legitimate completion. Here the failure mode is inverted but the same root defect class (an essential external verification treated as optional/bypassable) manifests as misattributed/unauthorized signup completion instead of blocked completion.

### Impact Explanation
If the `user_centric_signup` bypass is taken, a signup can be recorded as `Success` (`enroll_user::Status::Success`, `SignupStatus::Success`) purely from local pipeline state, without the backend's duplicate-detection and in-flight-match logic ever running. This can result in a misattributed or duplicate signup being accepted as valid (e.g., the same biometric identity completing multiple "successful" user-centric signups, or a signup racing another in-flight signup for the same identity) because the one authoritative cross-signup check (the backend poll) that exists specifically to catch these cases is skipped.

### Likelihood Explanation
`user_centric_signup` is populated from `backend::user_status::UserData` returned during QR validation and is a legitimate feature path (not requiring privileged access) — any unprivileged signup flow that goes through the "user-centric" branch takes this code path by design, and `detect_fraud` in this build is a no-op (`// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`), so `signup_reason` will be `Normal` in the overwhelming majority of cases, making the bypass path trivially reachable whenever this feature flag applies. However, I could not fully verify (given tool/index limits) how strictly `user_centric_signup` is gated server-side, or whether the FOSS `detect_fraud` stub is representative of the production (non-FOSS) build's real fraud-check integration — this uncertainty affects the practical exploitability assessment and should be confirmed against the production codebase.

### Recommendation
Do not let the `user_centric_signup` branch fully bypass backend verification. At minimum, still perform the backend enrollment/duplicate-check round trip (or an equivalent authoritative uniqueness check) before marking a user-centric signup as `Success`, and treat the local `signup_reason` as informational only, mirroring the corrected pattern from the C4 report which separated "informational" logging from a call that gates the security-relevant transition. If the `enroll_user` backend call cannot complete, the signup should not be recorded as authoritative success.

### Proof of Concept
Not applicable in ask-only mode — no code execution or test harness was run. The control-flow proof is the code cited above: when `user_centric_signup && !ignore_user_centric_signups` is true, `self.enroll_user(...)` (the only code path that contacts the backend enrollment/duplicate-detection endpoint) is never called, and `success` is set solely from the locally computed `signup_reason == SignupReason::Normal`, which — given `detect_fraud` is a stub returning `Ok(false)` in this build — will be true for essentially all completed pipelines.

### Citations

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

**File:** src/plans/enroll_user.rs (L157-176)
```rust
                            Ok(signup_poll::Response {
                                success: false,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
                                // This includes the following cases:
                                //   1. Backend duplicates
                                //   2. Backend legacy signup requests
                                //   3. Backend inflight matches
                                //   4. Backend detected fraud
                                //   5. Orb agent, internal, capture or pipeline failures
                                //   6. Orb detected fraud
                                tracing::info!("SIGNUP FAIL");
                                dd_incr!("main.count.http.user_enrollment.success.failed");
                                dd_incr!(
                                    "main.count.signup.result.failure.user_enrollment",
                                    "type:failure"
                                );
                                return Status::SignupVerificationNotSuccessful;
                            }
```
