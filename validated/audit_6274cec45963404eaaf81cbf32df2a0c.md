### Title
Backend duplicate/uniqueness enforcement is bypassed for "user-centric" signups, allowing the same biometric identity to be re-enrolled without ever consulting the authoritative dedup check - (File: `src/plans/mod.rs`)

### Summary
The `OlympusVotes` bug allowed a single unit of state (votes) to satisfy a threshold check twice because the enforcement decision trusted a locally re-derived balance instead of a value that was locked/consumed against an authoritative ledger. `MasterPlan::do_signup` in orb-core has the same root pattern for signup uniqueness enforcement: when a signup is flagged `user_centric_signup`, the orb determines enrollment `success` purely from its own locally computed `signup_reason` and never calls the backend enrollment endpoint that performs the real duplicate/uniqueness check.

### Finding Description
In `do_signup`, after biometric capture and the local pipeline/fraud check, the orb decides whether the enrollment succeeded: [1](#0-0) 

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

`signup_reason` is derived entirely on-device from `detect_fraud`/pipeline results (`src/plans/mod.rs:563-571`). When `user_centric_signup` is `true`, the `else` branch — the only branch that actually calls `enroll_user`, i.e. the branch that hits the backend `signup_post`/`signup_poll` endpoints — is skipped entirely.

The backend round trip in `enroll_user::Plan::run` is where the authoritative, cross-signup uniqueness/duplicate enforcement lives, as explicitly documented in the poll-response handling: [2](#0-1) 

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
    ...
    return Status::SignupVerificationNotSuccessful;
}
```

`user_centric_signup` is a boolean carried in `backend::user_status::UserData` sourced from the QR-code-linked `authenticated_app_data` (`src/backend/user_status.rs:203-212`), i.e. it originates from data supplied through the user's app/QR flow rather than being fixed, server-side, per-signup state that is consumed once. The Orb-local mitigating knob is `ignore_user_centric_signups` (an Orb config flag, not tied to the specific signup/identity), so absent that override every signup routed down the `user_centric_signup` path never reaches the one code path (`signup_post`/`signup_poll`) that checks whether this biometric identity (iris code / face fingerprint) has already been enrolled elsewhere. This is structurally the same defect class as the `OlympusVotes` finding: an authorization/threshold decision (“is this signup unique/allowed to succeed”) is made from a value that is not locked against — or re-validated by — the single authoritative source of truth (the backend’s duplicate registry), so the same underlying resource (a person’s biometric identity) can be used to satisfy the “successful, unique signup” condition repeatedly.

### Impact Explanation
Because `enroll_user` (and therefore `signup_post`/`signup_poll`, the only place that performs backend-side duplicate/fraud detection across all signups globally) is bypassed on the `user_centric_signup` path, a person could complete multiple “successful” signups with the same iris/biometric identity purely because the on-device fraud pipeline did not flag anything locally, even though the backend would have rejected the enrollment as a duplicate had it been consulted. This is a concrete cross-signup identity-uniqueness bypass: it defeats the core anti-Sybil / dedup guarantee of the signup system for any signup taking the user-centric branch, letting one identity be enrolled/attributed multiple times.

### Likelihood Explanation
This path is reached whenever `user_centric_signup` is `true` in the resolved `UserData` and the Orb’s `ignore_user_centric_signups` config is not set — i.e., the normal, default app-driven signup flow as coded, not a privileged or hardware-access precondition. No operator/peer/node compromise is required; the condition is driven by data associated with the ordinary unprivileged signup flow.

### Recommendation
Do not let the local pipeline/fraud outcome alone determine final enrollment `success` for `user_centric_signup` signups. Always perform (or asynchronously reconcile with) the backend `signup_post`/`signup_poll` uniqueness check before reporting a signup as ultimately successful/unique, and only use the local result to gate whether the enrollment attempt is submitted, not whether it is treated as authoritative and final.

### Proof of Concept
1. Complete a normal signup with `user_centric_signup = true` in the resolved `UserData` (`src/backend/user_status.rs:203-212`) and a biometric capture/pipeline that produces `SignupReason::Normal` locally.
2. Observe in `do_signup` (`src/plans/mod.rs:639-645`) that `success = true` is set without any call to `enroll_user`, hence without any call to `signup_post`/`signup_poll`.
3. Repeat step 1 with the same physical person/iris (same underlying biometric identity) under a different signup id / QR session, again with `user_centric_signup = true`.
4. Because `enroll_user` is never invoked in either run, the backend’s duplicate-detection logic documented at `src/plans/enroll_user.rs:162-168` (“Backend duplicates”, “Backend inflight matches”) is never exercised, and both signups are locally reported as `Status::Success` despite representing the same identity.

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
