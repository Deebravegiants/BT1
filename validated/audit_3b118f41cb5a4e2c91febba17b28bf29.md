Based on the code I found, there is a valid analog to this bug class in orb-core's signup-authorization flow.

### Title
Signup proceeds on a stale, un-revalidated user authorization snapshot instead of the state at time of use - (File: `src/plans/mod.rs`)

### Summary
The Unlock Protocol bug computes a refund using the *current* key price rather than the price that was actually snapshotted/paid, because the system never re-checks whether the snapshotted value is still valid at the moment it's actually used. `orb-core` has the same class of bug in its signup authorization path: the QR/backend-validated `UserData` (including cryptographic keys, `pcp_version`, and the `user_centric_signup` flag) is captured once during QR scanning and then reused, unchanged, for the entire remainder of the signup — including biometric capture, enrollment, and personal-custody-package upload — as long as an unrelated timer (`operator_qr_expiration_time`, up to 23 hours by default) hasn't expired. There is no re-validation of the user's authorization state at the point where it is actually consumed.

### Finding Description
In `scan_remaining_qr_codes` [1](#0-0) , when a `QrCodes::Both { operator_data, user_qr_code, user_data, .. }` tuple already exists and `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, the previously-fetched `user_data` is reused directly — the code never re-calls `backend::user_status::request` to confirm the user is still authorized, that the same keys are still valid, or that `user_centric_signup` still reflects the backend's current state.

That cached `user_data` was obtained earlier via `verify_user_qr_code` [2](#0-1) , which calls `backend::user_status::request` [3](#0-2)  only once at scan time.

The staleness window is gated purely by `operator_qr_expiration_time`, whose default is 23 hours: [4](#0-3) . This value is unrelated to whether the user's actual authorization/keys/fraud status is still current — it only bounds operator QR-code freshness, not user QR/backend-authorization freshness.

Downstream, `do_signup` [5](#0-4)  pulls the `user_centric_signup` flag directly from this potentially stale snapshot to decide enrollment success/failure without hitting the enrollment/fraud endpoint at all: [6](#0-5) . The same stale `user_data` (including `backend_iris_public_key`, `backend_face_public_key`, `pcp_version`, etc.) is also converted directly into `personal_custody_package::Credentials` used to build and upload the biometric package: [7](#0-6) .

This is structurally identical to the refund/price-snapshot bug: a value (`user_data`/authorization state) is captured at one point in time and used at a materially later point (post biometric capture / enrollment / PCP upload) in a security-relevant decision, without confirming it still reflects backend-side reality at time of use.

### Impact Explanation
If the backend revokes/changes a user's status, keys, or `user_centric_signup` designation between the initial QR validation and the actual enrollment/upload (which can be up to the full `operator_qr_expiration_time` window later, plus biometric capture time), orb-core will still complete the signup and upload a personal custody package using the stale authorization snapshot. This can result in misattributed or unauthorized signup completion (bypassing a backend-side authorization change) and the use of possibly-invalidated cryptographic keys for encrypting/uploading the user's biometric custody package.

### Likelihood Explanation
This requires no attacker sophistication — any unprivileged user simply needs to scan the QR codes and then wait/delay (idle scanning already supports a long window) before the biometric capture and enrollment portion of the flow completes, so backend-side state has time to change while the orb still holds and trusts the earlier snapshot. The wide default expiration window (23 hours) makes this an easily reachable condition in normal self-serve operation.

### Recommendation
Re-validate `user_data` (backend user status/authorization) immediately before it is used for a security-sensitive decision or action — i.e., right before enrollment (`enroll_user`) and right before building/uploading the personal custody package — rather than relying solely on the `operator_qr_expiration_time` staleness check on the operator tuple. Alternatively, track a separate, shorter freshness timestamp for `user_data` itself and force re-verification via `backend::user_status::request` whenever that threshold elapses before consuming it in `do_signup`.

### Proof of Concept
1. Start a self-serve signup; the orb scans the operator QR then the user QR, obtaining `user_data` via `verify_user_qr_code` (`src/plans/mod.rs:1580-1608`).
2. `scan_remaining_qr_codes` (`src/plans/mod.rs:788-820`) caches this `QrCodes::Both` tuple; as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time` (default 23h, `src/config.rs:443`), the tuple — including `user_data` — is reused verbatim on subsequent loop iterations/retries without calling `backend::user_status::request` again.
3. Meanwhile, suppose the backend invalidates or changes the user's authorization/keys/`user_centric_signup` flag (e.g., fraud flag raised, keys rotated) for that `user_id`.
4. `do_signup` proceeds to `enroll_user`/PCP building using the stale `user_data.user_centric_signup` and stale keys (`src/plans/mod.rs:639-656`, `1898-1938`), completing/uploading the signup as if the backend state had not changed, since no re-check occurs.

### Citations

**File:** src/plans/mod.rs (L572-573)
```rust
        let user_id = qr_codes.user_qr_code.user_id.clone();
        let user_centric_signup = qr_codes.user_data.user_centric_signup;
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

**File:** src/plans/mod.rs (L788-820)
```rust
    async fn scan_remaining_qr_codes(
        &mut self,
        orb: &mut Orb,
        qr_codes: QrCodes,
        operator_qr_expiration_time: Duration,
    ) -> Result<Option<ResolvedQrCodes>> {
        loop {
            match qr_codes {
                QrCodes::Both { operator_data, user_qr_code, user_data, user_qr_code_string }
                    if operator_data.timestamp.elapsed() < operator_qr_expiration_time =>
                {
                    break Ok(Some(ResolvedQrCodes {
                        operator_data,
                        user_qr_code,
                        user_data,
                        user_qr_code_string,
                    }));
                }
                QrCodes::Operator { operator_data }
                    if operator_data.timestamp.elapsed() < operator_qr_expiration_time =>
                {
                    let Some((user_qr_code, user_data, user_qr_code_string)) =
                        self.scan_user_qr_code(orb, &operator_data).await?
                    else {
                        break Ok(None);
                    };
                    break Ok(Some(ResolvedQrCodes {
                        operator_data,
                        user_qr_code,
                        user_data,
                        user_qr_code_string,
                    }));
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

**File:** src/plans/mod.rs (L1898-1938)
```rust
impl TryInto<personal_custody_package::Credentials> for ResolvedQrCodes {
    type Error = ();

    fn try_into(self) -> Result<personal_custody_package::Credentials, Self::Error> {
        let ResolvedQrCodes { operator_data, user_data, user_qr_code, user_qr_code_string } = self;
        if let (
            Some(backend_iris_public_key),
            Some(backend_iris_encrypted_private_key),
            Some(backend_normalized_iris_public_key),
            Some(backend_normalized_iris_encrypted_private_key),
            Some(backend_face_public_key),
            Some(backend_face_encrypted_private_key),
            Some(self_custody_user_public_key),
        ) = (
            user_data.backend_iris_public_key,
            user_data.backend_iris_encrypted_private_key,
            user_data.backend_normalized_iris_public_key,
            user_data.backend_normalized_iris_encrypted_private_key,
            user_data.backend_face_public_key,
            user_data.backend_face_encrypted_private_key,
            user_data.self_custody_user_public_key,
        ) {
            Ok(personal_custody_package::Credentials {
                operator_qr_code: operator_data.qr_code,
                user_qr_code,
                user_qr_code_string,
                backend_iris_public_key,
                backend_iris_encrypted_private_key,
                backend_normalized_iris_public_key,
                backend_normalized_iris_encrypted_private_key,
                backend_face_public_key,
                backend_face_encrypted_private_key,
                backend_tier2_public_key: user_data.backend_tier2_public_key,
                backend_tier2_encrypted_private_key: user_data.backend_tier2_encrypted_private_key,
                self_custody_user_public_key,
                pcp_version: user_data.pcp_version,
            })
        } else {
            Err(())
        }
    }
```

**File:** src/backend/user_status.rs (L145-163)
```rust
/// Makes a validation request.
#[allow(clippy::too_many_lines)]
pub async fn request(
    qr_code: &qr_scan::user::Data,
    operator_data: &OperatorData,
    use_full_operator_qr: bool,
    use_only_operator_location: bool,
) -> Result<Option<UserData>> {
    let Response { valid, reason, backend_keys, authenticated_app_data } =
        do_request(qr_code, operator_data, use_full_operator_qr, use_only_operator_location)
            .await?;
    if !valid {
        tracing::info!(
            "User QR-code invalid: {qr_code:?}, reason: {:?}",
            reason.as_deref().unwrap_or("<empty>")
        );
        return Ok(None);
    }
    if let (Some(backend_keys), Some(user_data)) = (backend_keys, authenticated_app_data) {
```

**File:** src/config.rs (L443-443)
```rust
            operator_qr_expiration_time: Duration::from_secs(60 * 60 * 23),
```
