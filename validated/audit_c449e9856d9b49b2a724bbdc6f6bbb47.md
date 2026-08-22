### Title
Local biometric enrollment success is recorded without backend confirmation for "user-centric" signups, bypassing server-side fraud/duplicate checks - ([File: src/plans/mod.rs])

### Summary
In `do_signup`, when `user_centric_signup` is true (a flag set by the backend/app QR data, not the operator) and `ignore_user_centric_signups` is not set, the Orb marks the signup as `Success`/`enroll_user::Status::Success` purely from local state (whether the biometric pipeline ran and fraud wasn't locally detected), completely skipping the `enroll_user::Plan` call that would otherwise POST to `signup_post::request` and poll `signup_poll::request` for backend confirmation.

### Finding Description
The relevant branch is: [1](#0-0) 

```rust
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups {
    debug_report.enrollment_status(match signup_reason {
        SignupReason::Normal => enroll_user::Status::Success,
        _ => enroll_user::Status::Error,
    });
    signup_reason == SignupReason::Normal
} else {
    Box::pin(self.enroll_user(orb, debug_report, &capture, pipeline.as_ref(), signup_reason)).await.is_success()
};
```

`user_centric_signup` originates from `authenticated_app_data` decoded from the QR-linked backend response in `src/backend/user_status.rs` (`orb_qr_link::UserData::user_centric_signup`), i.e., it's attacker/app-influenced context, not an Orb-verified fact about backend enrollment state. [2](#0-1) 

Normally, `enroll_user::Plan::run` is the only code path that talks to the backend `signup_post`/`signup_poll` endpoints, which perform authoritative checks (duplicate iris detection, backend fraud detection, "inflight matches", legacy signup handling) as documented in the poll response handling: [3](#0-2) 

When `user_centric_signup` is true, this entire backend confirmation step is skipped, and `SignupReason::Normal` (a purely local determination based on `pipeline.is_some()` and local `detect_fraud` result) is treated as equivalent to a backend-confirmed `Success`. This is directly analogous to the reported bug class: the code assumes a critical remote operation ("commit"/verification with the backend) succeeded, and proceeds to record the deposit/enrollment as successful, without actually confirming it did.

### Impact Explanation
If the local pipeline/fraud reasoning is bypassable or simply wrong (e.g., `detect_fraud` is a no-op per the FOSS build: `// FOSS: WE HAVE DELETED ALL FRAUD CHECKS` at src/plans/mod.rs:1403), a signup can be locally recorded and reported as `Success` (triggering `enrollment_status` = `Success`, `debug_report.signup_successful()`, and success UI/telemetry) without ever being validated, deduplicated, or fraud-checked by the backend. This is a misattributed/unauthorized-signup class impact: a person could be credentialed by the Orb as a unique verified human locally while the backend — the actual source of truth for uniqueness/fraud — never confirmed (or possibly would have rejected) the enrollment. [4](#0-3) 

### Likelihood Explanation
`user_centric_signup` is sourced from backend/app-provided QR user data, and the whole bypass is gated by a single boolean plus a config flag (`ignore_user_centric_signups`) that must be disabled/default. Given `detect_fraud` currently performs no checks in this build, the "local" fraud gate offers no real protection, making the bypass condition (`SignupReason::Normal`) trivially satisfied whenever biometric capture and pipeline succeed. No special privileges are required beyond a normal signup flow with a QR code that sets `user_centric_signup: true`.

### Recommendation
Do not treat `user_centric_signup` as sufficient to bypass backend confirmation of enrollment success. At minimum, still call/await an authoritative backend endpoint (equivalent to `enroll_user::Plan`/`signup_post`+`signup_poll`) to confirm the signup was accepted server-side before recording `enrollment_status(Success)` and reporting `signup_successful()`, mirroring the remediation pattern for the reported bug (never assume success on an operation whose result wasn't actually checked/confirmed). If the "user-centric" flow is intentionally designed for app-side confirmation, ensure there is an equivalent Orb-side backend round-trip (with retries) that can return failure and prevent local success attribution — analogous to using `safeTransfer`/checked calls rather than assuming success.

### Proof of Concept
1. An app/backend-controlled QR payload sets `authenticated_app_data.user_centric_signup = true` (decoded in `src/backend/user_status.rs::request`).
2. Orb performs biometric capture; pipeline is produced (`pipeline.is_some()`), and since `detect_fraud` is a no-op (src/plans/mod.rs:1390-1406), `fraud_detected` is always `false`, so `signup_reason == SignupReason::Normal`.
3. In `do_signup` (src/plans/mod.rs:639-656), because `user_centric_signup` is `true` and `ignore_user_centric_signups` is `false` (default), the code sets `enrollment_status(Success)` and `success = true` without ever invoking `enroll_user::Plan::run`, i.e., without any `signup_post`/`signup_poll` round trip to the backend.
4. `report_signup_reason` marks `debug_report.signup_successful()` and increments `main.count.signup.result.success.successful_signup`, and the UI shows signup success — all without backend-side verification, duplicate detection, or fraud checks having ever run for this signup.

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

**File:** src/plans/mod.rs (L1403-1406)
```rust
        // FOSS: WE HAVE DELETED ALL FRAUD CHECKS

        Ok(false)
    }
```

**File:** src/backend/user_status.rs (L203-212)
```rust
        let orb_qr_link::UserData {
            identity_commitment,
            self_custody_public_key: user_public_key,
            #[cfg(feature = "internal-data-acquisition")]
            data_policy,
            pcp_version,
            user_centric_signup,
            orb_relay_app_id,
            ..
        } = user_data;
```

**File:** src/plans/enroll_user.rs (L156-176)
```rust
                            }
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
