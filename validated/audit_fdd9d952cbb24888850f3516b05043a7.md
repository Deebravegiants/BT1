### Title
Stale backend authorization reused for signup without re-validation - ([File: src/plans/mod.rs])

### Summary
The reported LidoVault bug is a "compute-once, use-later-without-recheck" flaw: `adminSettleDebtAmount` is fixed at `initiatingAdminSettleDebt()` and then blindly consumed at `adminSettleDebt()` even though the underlying state (withdrawable balances) can change during the timelock, causing the finalized action to be based on stale data. The same bug class exists in `scan_remaining_qr_codes` in `src/plans/mod.rs`: a previously fetched `backend::user_status::UserData` (identity/authorization data obtained from the backend at QR-scan time) is reused at actual signup time, gated only by a client-side timer (`operator_qr_expiration_time`) rather than a fresh backend re-check.

### Finding Description
When a user QR-code has already been scanned and validated during idle scanning (`idle_scan_user_qr_code` → `handle_user_qr_code` → `verify_user_qr_code` → `backend::user_status::request`), the resulting `UserData` (containing `id_commitment`, `self_custody_user_public_key`, backend encryption keys, `user_centric_signup`, etc.) is cached in the `QrCodes::Both` variant [1](#0-0) .

Later, in `scan_remaining_qr_codes`, if `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, the cached `user_data` is returned directly and used for the rest of the signup flow (`build_pcp`, `enroll_user`, `signup_post::request`) **without calling `verify_user_qr_code`/`backend::user_status::request` again**: [2](#0-1) 

The only guard against staleness is a local `Instant` timer comparison, not a backend re-validation call: [3](#0-2) 

Meanwhile, `backend::user_status::request` is the sole authority for whether a user QR-code is `valid` (i.e., not banned/fraud-flagged/revoked) and for producing the `id_commitment` bound to the signup: [4](#0-3) 

Because the whole biometric capture pipeline (`biometric_capture`, `biometric_pipeline`, PCP building, and `signup_post::request`) can take a non-trivial amount of wall-clock time (multiple network calls, model inference, retries with `POLL_STATUS_COUNT` × `POLL_STATUS_INTERVAL` polling, etc., cf. `enroll_user::Plan::run`) [5](#0-4) , and because the reuse path in `scan_remaining_qr_codes` is triggered any time the operator QR is still within its expiration window, the orb can proceed to bind biometric capture data and issue a signup POST using authorization state (`id_commitment`, `self_custody_user_public_key`, validity) that was fetched once and never re-confirmed with the backend for the actual moment of finalization — directly analogous to `adminSettleDebt()` using a stale `adminSettleDebtAmount` computed at `initiatingAdminSettleDebt()` time instead of re-checking the live state at finalization.

### Impact Explanation
If the backend revokes/invalidates a user's session, flags fraud, or updates `id_commitment`/keys between the initial idle QR validation and the actual signup POST, orb-core will still proceed with the stale, already-cached authorization instead of re-checking with the backend, potentially completing a signup that the backend would no longer consider valid at finalization time. This is a cross-time state mismatch between what was authorized and what is ultimately submitted/bound (misattributed/unauthorized signup finalization), the same "commit based on stale computed value that the counterparty state has since moved past" pattern as the LidoVault report.

### Likelihood Explanation
Medium: this path is reachable by an ordinary (unprivileged) signup flow every time the operator QR-code has not yet expired (`operator_qr_expiration_time` window) when `scan_remaining_qr_codes` is invoked for `QrCodes::Both`/`QrCodes::Operator`. No special privilege or attacker capability beyond normal timing (waiting for the backend to change user status mid-flow) is required.

### Recommendation
Re-validate (or at minimum re-check validity/authorization freshness, not just re-use the cached response) via `backend::user_status::request` immediately before finalizing the signup (i.e., right before `signup_post::request` / `build_pcp`), rather than solely relying on a local expiration timer to decide whether to reuse previously fetched `UserData`. This closes the window during which backend-side revocation/fraud decisions can be silently bypassed by locally cached authorization data.

### Proof of Concept
1. User scans operator QR and user QR during idle scanning; `backend::user_status::request` returns `valid: true` with `UserData` (id_commitment X), cached into `QrCodes::Both`.
2. Backend subsequently marks this `user_id`/session invalid or fraudulent (e.g., a moderation action) before `operator_qr_expiration_time` elapses.
3. `do_signup` calls `scan_remaining_qr_codes`, hits the `QrCodes::Both { .. } if operator_data.timestamp.elapsed() < operator_qr_expiration_time` branch, and returns the stale cached `user_data` without any backend re-check.
4. The orb proceeds through biometric capture/pipeline and issues `signup_post::request` bound to the stale `id_commitment`/authorization, completing a signup the backend would have rejected had it been asked at finalization time.

### Citations

**File:** src/plans/mod.rs (L144-157)
```rust
#[allow(clippy::large_enum_variant)]
#[derive(Clone)]
enum QrCodes {
    Both {
        operator_data: OperatorData,
        user_qr_code: qr_scan::user::Data,
        user_data: backend::user_status::UserData,
        user_qr_code_string: String,
    },
    Operator {
        operator_data: OperatorData,
    },
    None,
}
```

**File:** src/plans/mod.rs (L794-820)
```rust
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

**File:** src/plans/mod.rs (L1888-1895)
```rust
    fn operator_timestamp(&self) -> Option<Instant> {
        match self {
            QrCodes::Operator { operator_data } | QrCodes::Both { operator_data, .. } => {
                Some(operator_data.timestamp)
            }
            QrCodes::None => None,
        }
    }
```

**File:** src/backend/user_status.rs (L152-245)
```rust
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
        tracing::info!("User QR-data: {user_data:?}");

        #[cfg(not(feature = "skip-user-qr-validation"))]
        {
            let Some(user_data_hash) = &qr_code.user_data_hash else {
                tracing::error!(
                    "image_self_custody is provided by backend, but got no user_data_hash from \
                     QR-code"
                );
                return Ok(None);
            };
            if !user_data.verify(user_data_hash) {
                tracing::error!("user_data verification failure");
                return Ok(None);
            }
        }

        let BackendKeys {
            iris:
                BackendKey {
                    public_key: backend_iris_public_key,
                    encrypted_private_key: backend_iris_encrypted_private_key,
                },
            normalized_iris:
                BackendKey {
                    public_key: backend_normalized_iris_public_key,
                    encrypted_private_key: backend_normalized_iris_encrypted_private_key,
                },
            face:
                BackendKey {
                    public_key: backend_face_public_key,
                    encrypted_private_key: backend_face_encrypted_private_key,
                },
            tier2: backend_tier2,
        } = backend_keys;
        let backend_tier2_public_key =
            backend_tier2.as_ref().map(|backend_tier2| backend_tier2.public_key.as_str());
        let backend_tier2_encrypted_private_key =
            backend_tier2.as_ref().map(|backend_tier2| backend_tier2.encrypted_private_key.clone());
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
        let backend_iris_public_key = decode_public_key(&backend_iris_public_key)
            .wrap_err("decoding backend_iris_public_key")?;
        let backend_normalized_iris_public_key =
            decode_public_key(&backend_normalized_iris_public_key)
                .wrap_err("decoding backend_normalized_iris_public_key")?;
        let backend_face_public_key = decode_public_key(&backend_face_public_key)
            .wrap_err("decoding backend_face_public_key")?;
        let backend_tier2_public_key = backend_tier2_public_key
            .map(decode_public_key)
            .transpose()
            .wrap_err("decoding backend_tier2_public_key")?;
        let user_public_key =
            decode_public_key(&user_public_key).wrap_err("decoding user_public_key")?;
        Ok(Some(UserData {
            backend_iris_public_key: Some(backend_iris_public_key),
            backend_iris_encrypted_private_key: Some(backend_iris_encrypted_private_key),
            backend_normalized_iris_public_key: Some(backend_normalized_iris_public_key),
            backend_normalized_iris_encrypted_private_key: Some(
                backend_normalized_iris_encrypted_private_key,
            ),
            backend_face_public_key: Some(backend_face_public_key),
            backend_face_encrypted_private_key: Some(backend_face_encrypted_private_key),
            backend_tier2_public_key,
            backend_tier2_encrypted_private_key,
            self_custody_user_public_key: Some(user_public_key),
            id_commitment: Some(identity_commitment),
            #[cfg(feature = "internal-data-acquisition")]
            data_policy,
            pcp_version,
            user_centric_signup,
            orb_relay_app_id,
        }))
    } else {
```

**File:** src/plans/enroll_user.rs (L90-153)
```rust
        let signup_id = self.signup_id.to_string();
        for i in 0..RETRIES_COUNT {
            let response = signup_post::request(
                signature.as_ref(),
                &signup_id,
                &self.operator_qr_code,
                &self.user_qr_code,
                &self.s3_region_str,
                self.capture,
                self.pipeline,
                self.signup_reason,
            )
            .await;
            match response {
                Ok(signup_post::Response {
                    software_version_status:
                        versions @ (signup_post::SoftwareVersionStatus::Allowed
                        | signup_post::SoftwareVersionStatus::Deprecated
                        | signup_post::SoftwareVersionStatus::Unknown
                        | signup_post::SoftwareVersionStatus::Empty),
                }) => {
                    if matches!(versions, signup_post::SoftwareVersionStatus::Deprecated) {
                        tracing::warn!("Orb component versions are deprecated");
                        notify_failed_signup(
                            orb,
                            Some(SignupFailReason::SoftwareVersionDeprecated),
                        );
                    }
                    if matches!(versions, signup_post::SoftwareVersionStatus::Empty)
                        || matches!(versions, signup_post::SoftwareVersionStatus::Unknown)
                    {
                        tracing::warn!("Backend doesn't know this software version.");
                        tracing::warn!(
                            "This is considered a deprecated version on staging builds, and \
                             blocked on prod."
                        );
                        #[cfg(feature = "stage")]
                        notify_failed_signup(
                            orb,
                            Some(SignupFailReason::SoftwareVersionDeprecated),
                        );
                        #[cfg(not(feature = "stage"))]
                        return Status::SoftwareVersionUnknown;
                    }
                    for i in 0..POLL_STATUS_COUNT {
                        sleep(POLL_STATUS_INTERVAL).await;
                        #[cfg(not(feature = "ui-test-successful-signup"))]
                        let response = signup_poll::request(&signup_id).await;

                        #[cfg(feature = "ui-test-successful-signup")]
                        let response: Result<signup_poll::Response> = Ok(signup_poll::Response {
                            status: signup_poll::Status::Completed,
                            success: true,
                            error: None,
                        });

                        match response {
                            Ok(signup_poll::Response {
                                success: true,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
                                tracing::info!("SIGNUP SUCCESS");
                                dd_incr!("main.count.http.user_enrollment.success.success_unique");
```
