### Title
Stale "signup session" authorization used to finalize enrollment without backend re-verification, enabling cross-signup state bleed for user-centric signups - (File: src/plans/mod.rs)

### Summary
The reported bug class is a TOCTOU/"stale check" issue: a value (`maxLp`) is validated once, but the privileged action (`setPerTokenWalletCap`) is executed later, after an unprivileged actor has changed the underlying state, breaking the invariant the check was meant to enforce. The analogous pattern exists in `orb-core`'s signup flow: the "is this signup session unique/authorized" determination (`user_centric_signup`) is fetched once from the backend at QR-scan time via `verify_user_qr_code`, cached, and then used much later — after a multi-step, multi-second/minute biometric capture and pipeline — to decide whether the Orb should skip backend enrollment/dedup verification entirely and just locally declare `success`.

### Finding Description
`verify_user_qr_code` (T1) queries `backend::user_status::request` and returns a `UserData` struct that includes `user_centric_signup: bool` [1](#0-0) . This value is captured once, early in the flow (during idle QR scanning), and stored in `qr_codes.user_data`.

Later, in `do_signup` (T2), after `start_signup`, QR re-validation, a fixed 3-second sleep, `biometric_capture`, and the full `biometric_pipeline` (all of which can take a non-trivial, variable amount of time), the cached `user_centric_signup` flag from T1 is read out and used to branch: [2](#0-1) 

For the `user_centric_signup && !ignore_user_centric_signups` branch, the Orb **never calls the backend enrollment endpoint** (`enroll_user`, which performs `signup_post`/`signup_poll` — the path that does duplicate/fraud/inflight-match detection on the backend, as documented in `src/plans/enroll_user.rs` lines 162-168 "Backend duplicates ... Backend inflight matches"). Instead, it locally sets `success = signup_reason == SignupReason::Normal`, relying entirely on the local pipeline's fraud/liveness result and the stale, T1-time backend flag.

This mirrors the `setPerTokenWalletCap` bug precisely: a state check (`user_centric_signup`/session validity, analogous to `getMaxCommunityLpPositon`) is performed once, and a consequential action (skipping backend dedup and unilaterally declaring enrollment success, analogous to `setPerTokenWalletCap`) is performed at a later time, without re-validating that the invariant the original check protected (only one authoritative enrollment/session outcome per user QR session) still holds. In between T1 and T2, nothing prevents an unprivileged actor (the person being enrolled, or anyone controlling the paired mobile app/session) from performing ordinary, permitted actions — e.g., presenting/re-using the same user QR session at a second Orb in parallel, or restarting the app-side flow — because the uniqueness/authorization check the flag represents is not re-confirmed against the backend at commit time.

### Impact Explanation
Because the user-centric branch bypasses `enroll_user`'s backend round trip (which is the actual place duplicate/inflight signups are rejected per the comments in `enroll_user.rs`), two concurrent or sequential capture attempts using the same stale `user_centric_signup=true` session can each independently reach the local "success" branch on different Orbs (or on retries) without the backend ever being asked to arbitrate. This is a cross-signup state bleed / misattributed-signup risk: the record of "success" and the biometric package uploads (tier0/tier1/tier2, sent unconditionally before this branch decision) are not gated by a fresh authorization check, meaning the actual protection against duplicate or split enrollment for this signup mode depends solely on a value read once at QR-scan time and never re-checked before the Orb commits to a locally-declared successful enrollment.

### Likelihood Explanation
Reaching this code path requires no privilege beyond being the ordinary signed-up user themselves — no admin/operator role or malicious node assumption is needed, satisfying the "unprivileged user analog" requirement. The race window is naturally created by the multi-second sleep plus full biometric capture and pipeline processing between the T1 check and the T2 use, giving a realistic, non-bot-frontrunning window analogous to the original report's "poor timing" scenario.

### Recommendation
Before committing to `success = signup_reason == SignupReason::Normal` in the `user_centric_signup` branch, re-verify the session/authorization state with the backend (e.g., a fresh `user_status` or equivalent check) rather than relying solely on the value cached at QR-scan time, so that the same invariant enforced for non-user-centric signups (via `enroll_user`'s duplicate/inflight detection) also applies here.

### Proof of Concept
1. User presents their QR/session data to Orb A; `verify_user_qr_code` returns `user_centric_signup = true`, cached in `qr_codes.user_data`.
2. Before Orb A completes its multi-second biometric capture + pipeline, the same user (or app-controlled session) is presented to Orb B, which independently performs the same T1 check and also caches `user_centric_signup = true`.
3. Both Orb A and Orb B proceed through capture/pipeline and, in `do_signup`, both take the `user_centric_signup` branch, each locally declaring `success = true` based only on their own local fraud/liveness result — neither round-trips to the backend for enrollment/dedup arbitration.
4. Both Orbs report a successful signup for the same user session, with no backend-side reconciliation between the two, evidencing the stale-check/cross-signup bleed described in the finding: [3](#0-2) .

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

**File:** src/plans/mod.rs (L1580-1608)
```rust
    /// Checks if `qr_code` is a valid user QR-code through the backend.
    async fn verify_user_qr_code(
        &self,
        orb: &mut Orb,
        user_qr_code: &qr_scan::user::Data,
        operator_data: &OperatorData,
        qr_capture_start: Option<Instant>,
    ) -> Result<Option<backend::user_status::UserData>> {
        let Config {
            user_qr_validation_use_full_operator_qr,
            user_qr_validation_use_only_operator_location,
            ..
        } = *orb.config.lock().await;
        match backend::user_status::request(
            user_qr_code,
            operator_data,
            user_qr_validation_use_full_operator_qr,
            user_qr_validation_use_only_operator_location,
        )
        .await
        {
            Ok(Some(user_data)) => {
                orb.ui.qr_scan_success(QrScanSchema::User);
                dd_incr!("main.count.signup.during.general.user_qr_code_validate");
                tracing::info!("User QR-code validated: {user_qr_code:?}");
                if let Some(qr_capture_start) = qr_capture_start {
                    dd_timing!("main.time.signup.user_qr_code_capture", qr_capture_start);
                }
                return Ok(Some(user_data));
```
