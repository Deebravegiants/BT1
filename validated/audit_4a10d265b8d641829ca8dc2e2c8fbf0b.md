### Title
Signup is marked `Success` locally without any backend confirmation that enrollment actually completed - (File: `src/plans/mod.rs`)

### Summary
`MasterPlan::do_signup` treats a signup as successfully enrolled purely based on a locally-computed `signup_reason`, without ever calling the backend enrollment endpoint to confirm that the identity was actually bound/enrolled, whenever the QR-scanned user data indicates `user_centric_signup`. This mirrors the referenced NFT bug pattern: the "transaction" (signup) is reported as `Success` and the biometric personal-custody package (PCP) has already been uploaded, but the step that is supposed to actually confirm the critical action happened — server-side enrollment/verification — is skipped entirely.

### Finding Description
In `do_signup`, after biometric capture, pipeline execution, and fraud detection, the code computes `signup_reason` (`Normal`, `Fraud`, or `Failure`) purely from local pipeline/fraud results: [1](#0-0) 

It then builds and uploads the PCP tier-0 package unconditionally (regardless of whether fraud was detected), and only afterward decides whether the signup counts as a success: [2](#0-1) 

When `user_centric_signup` is `true` (a flag taken from the backend-signed `authenticated_app_data` embedded in the user's QR code, see `UserData::user_centric_signup` in `src/backend/user_status.rs`), the branch at line 639-645 never calls `self.enroll_user(...)` — the function that actually performs the network request to the signup backend (`signup_post::request` + polling `signup_poll::request`) and waits for the backend's `Completed`/`success: true` response (`src/plans/enroll_user.rs`). Instead, `enrollment_status` is set to `enroll_user::Status::Success` solely because `signup_reason == SignupReason::Normal`, i.e., because the orb's own local checks passed. This is the direct analog of `_transferNFTs()` returning success without ever performing the transfer: the "signup completed / enrollment succeeded" status is recorded and reported to the UI/App and to `debug_report.signup_successful()` without any confirmation from the trusted counterparty (the backend) that enrollment/identity-binding was actually persisted.

By contrast, the non-`user_centric_signup` path calls `enroll_user`, which does perform this backend round-trip and only reports `Status::Success` after the backend explicitly returns `Completed`/`success: true` (`src/plans/enroll_user.rs`, lines 134-156).

### Impact Explanation
If the backend never receives/records a completed enrollment for a `user_centric_signup` flow (e.g., backend outage, dropped connection, backend-side rejection, or a compromised/forged `user_centric_signup=true` flag in the app-signed payload), the orb will still locally report `Status::Success`, `signup_successful()`, and `SignupEnded { success: true }` to the app via `orb_relay` (`src/plans/mod.rs`, lines 1485-1495), while the biometric PCP tier-0 package has already been uploaded to the backend storage. This can result in a misattributed/unconfirmed signup: the user is told they are verified, and the biometric data is sent, but there is no guaranteed server-side confirmation that the signup was correctly bound to the intended identity commitment/wallet — directly analogous to the referenced bug where a sale is marked successful while the underlying asset transfer never occurred.

### Likelihood Explanation
`user_centric_signup` is a normal, backend-configurable flow (governed by `Config::ignore_user_centric_signups`, default `false`, see `src/config.rs` line 436), meaning this code path is reachable in production without any attacker action — it triggers whenever the backend/app indicates a user-centric signup and is not overridden by `ignore_user_centric_signups`. No exploit is required to reach the branch; it depends only on backend/app-controlled data already trusted elsewhere in the same request.

### Recommendation
Do not derive `enrollment_status` for `user_centric_signup` solely from the orb-local `signup_reason`. Perform an authoritative round-trip to the backend enrollment/signup-status endpoint (as done in the non-user-centric path via `enroll_user`) before marking `Status::Success`, or otherwise require an explicit backend acknowledgment that the enrollment/identity binding was persisted prior to reporting success to the UI/app and building/uploading the PCP.

### Proof of Concept
1. Configure the backend/app so `authenticated_app_data.user_centric_signup = true` for a signup QR code, and ensure `ignore_user_centric_signups` remains `false` (default).
2. Complete biometric capture and pipeline such that no fraud is detected (`signup_reason == SignupReason::Normal`), while the actual backend enrollment call is never made (this branch skips `enroll_user` entirely).
3. Observe that `success` is computed as `true` purely from `signup_reason == SignupReason::Normal` at `src/plans/mod.rs` lines 639-645, causing `debug_report.signup_successful()` and `result.success = true` to be set and reported via `SignupEnded { success: true }`, with no backend confirmation ever obtained that the enrollment was actually completed/recorded.

### Citations

**File:** src/plans/mod.rs (L563-571)
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
