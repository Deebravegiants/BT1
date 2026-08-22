## Title
Orb declares signup enrollment "successful" without confirming backend-side completion when `user_centric_signup` is set - (File: `src/plans/mod.rs`)

### Summary
In the same way the Turnstile `register()`/`RegisterEvent` mismatch let the application layer treat a registration as successful while the stricter consensus-layer check silently rejected it (with no way to redo the one-time action), `orb-core`'s `MasterPlan::do_signup` treats a signup as **enrolled/successful purely on the Orb's own local judgement** (pipeline ran, no local fraud detected) when `user_centric_signup` is set, **without ever calling the backend's actual enrollment-confirmation flow** (`enroll_user::Plan::run`, which posts the signature/iris codes and polls `signup_poll` until the backend explicitly reports `Status::Completed && success == true`). This is a strictness mismatch between the local ("app/orb") layer and the authoritative backend layer, and because a signup is a one-shot, non-repeatable action, a legitimate user can be told the signup succeeded (UI/dbus/debug-report marked `Success`) while the backend never actually completed/confirmed enrollment.

### Finding Description
`MasterPlan::do_signup` decides `signup_reason` (`Normal`/`Fraud`/`Failure`) purely from local checks: whether the biometric `pipeline` produced a result and whether `detect_fraud` (an Orb-local check) flagged fraud [1](#0-0) . It then builds and uploads the Personal Custody Package (PCP) to the backend [2](#0-1) .

Immediately after, the code decides "success" for `user_centric_signup` orbs *without* asking the backend whether the enrollment record was actually created/committed:

```rust
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
{
    debug_report.enrollment_status(match signup_reason {
        SignupReason::Normal => enroll_user::Status::Success,
        _ => enroll_user::Status::Error,
    });
    signup_reason == SignupReason::Normal
} else {
    Box::pin(self.enroll_user(orb, debug_report, &capture, pipeline.as_ref(), signup_reason))
        .await
        .is_success()
};
``` [3](#0-2) 

Contrast this with the `else` branch (`enroll_user::Plan::run`), which is the actual stricter/authoritative check: it POSTs the signup to the backend and polls `signup_poll::request` in a loop, only returning `Status::Success` when the backend explicitly reports `success: true` and `status: Completed` — otherwise it returns failures for duplicates, in-flight matches, backend-detected fraud, or server errors [4](#0-3) .

`user_centric_signup` is a boolean supplied by the backend/QR flow (`orb_qr_link::UserData.user_centric_signup`) and simply passed through into `UserData` [5](#0-4) ; the config flag `ignore_user_centric_signups` is the only guard, defaulting to `false` [6](#0-5) .

Furthermore, note that the PCP upload itself is best-effort: if `qr_codes.try_into()` fails to produce `credentials`, the whole PCP-build/upload block is skipped silently (`if let Ok(...) = ... { ... }` with no `else`) [7](#0-6) , yet the `success` determination that follows is completely independent of whether that block ran or its outcome — it only depends on `user_centric_signup` and the Orb's local `signup_reason`.

This exactly parallels the reported bug class: a looser, locally-satisfied condition (`pipeline.is_some() && !fraud_detected`) is used as a stand-in for a stricter, authoritative confirmation (backend's actual biometric enrollment/dedup pipeline reachable only via `enroll_user`'s poll loop), and the discrepancy is silent — no error is surfaced, the UI reports success (`ui_complete_signup` renders `SignupStatus::Success`) [8](#0-7) , and the signup session/id cannot be replayed since a new `SignupId` and full biometric capture would be required.

### Impact Explanation
A user whose Orb takes the `user_centric_signup` path can be told their signup/verification succeeded (locally-derived `Status::Success`, debug report marked `signup_successful()`, UI shows success) even though the backend's authoritative enrollment/fraud/dedup pipeline was never actually confirmed to have completed for that biometric capture. This is a cross-layer trust mismatch causing misattributed/false-positive signup completion — analogous to a registered contract silently failing on the consensus layer while the app layer reports it as done. Because signup is effectively one-shot per capture, there is no automatic mechanism shown in this code path to detect or retry the mismatch.

### Likelihood Explanation
This path is reachable by any unprivileged end user going through the app-centric/self-serve signup flow whenever the backend returns `user_centric_signup: true` for their session (the default production condition for app-centric flows, gated only by `ignore_user_centric_signups`, which defaults to `false`). No special privileges, hardware access, or malicious peer/operator behavior is needed — it is a straightforward, always-available code path for that signup mode.

### Recommendation
Do not derive `success`/`enrollment_status` purely from local Orb-side `signup_reason` when `user_centric_signup` is set. Either always confirm completion with the backend before marking the debug report and UI as `Success` (e.g., still require a poll/confirmation acknowledging the PCP packages were accepted and processed), or ensure the app-side flow that owns confirmation is verified to have actually reported success back to the Orb (e.g., via `orb_relay`) before `report_signup_reason`/`ui_complete_signup` treat the signup as successful.

### Proof of Concept
1. User completes biometric capture on an Orb where the backend flags their QR session `user_centric_signup: true`.
2. Local pipeline succeeds and `detect_fraud` finds no local fraud → `signup_reason == SignupReason::Normal`.
3. PCP package upload block silently fails to run (e.g. `qr_codes.try_into()` fails) or succeeds but is not actually confirmed processed by backend.
4. `do_signup` still executes:
```rust
let success = if user_centric_signup && !ignore_user_centric_signups {
    debug_report.enrollment_status(enroll_user::Status::Success); // unconditional given Normal
    signup_reason == SignupReason::Normal // true
} else { ... };
``` [3](#0-2) 
5. `report_signup_reason` marks `debug_report.signup_successful()` and increments the success metric [9](#0-8) ; the UI later renders `orb.ui.signup_success()` [10](#0-9)  — without the backend's `enroll_user`-style poll ever having confirmed that the enrollment record actually exists on the backend.

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

**File:** src/plans/mod.rs (L574-637)
```rust
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
            data_uploader::wait_queues(orb.data_uploader.enabled().unwrap()).await?;
            if !self
                .upload_pcp_tier_0(
                    orb,
                    &result.signup_id,
                    &user_id,
                    packages.tier0,
                    packages.tier0_checksum,
                    if pcp_version >= 3 { Some(0) } else { None },
                )
                .await?
            {
                return Ok(result);
            }
            if pcp_version >= 3 {
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id: user_id.clone(),
                        data: packages.tier1,
                        checksum: packages.tier1_checksum.as_ref().to_vec(),
                        tier: 1,
                    })))
                    .await?;
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id,
                        data: packages.tier2,
                        checksum: packages.tier2_checksum.as_ref().to_vec(),
                        tier: 2,
                    })))
                    .await?;
            }
        }
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

**File:** src/plans/mod.rs (L676-678)
```rust
        } else if success {
            debug_report.signup_successful();
            dd_incr!("main.count.signup.result.success.successful_signup");
```

**File:** src/plans/mod.rs (L1500-1506)
```rust
    fn ui_complete_signup(
        orb: &mut Orb,
        signup_status: &debug_report::SignupStatus,
        enrollment_status: Option<enroll_user::Status>,
    ) {
        match signup_status {
            SignupStatus::Success => orb.ui.signup_success(),
```

**File:** src/plans/enroll_user.rs (L146-176)
```rust
                        match response {
                            Ok(signup_poll::Response {
                                success: true,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
                                tracing::info!("SIGNUP SUCCESS");
                                dd_incr!("main.count.http.user_enrollment.success.success_unique");
                                dd_incr!("main.count.http.user_enrollment.success.success");
                                return Status::Success;
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

**File:** src/backend/user_status.rs (L203-244)
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
```

**File:** src/config.rs (L383-437)
```rust
impl Default for Config {
    fn default() -> Self {
        Self {
            basic_config: BasicConfig { sound_volume: DEFAULT_SOUND_VOLUME, language: None },
            operation_country: if cfg!(feature = "stage") { Some("DEV".to_owned()) } else { None },
            operation_city: if cfg!(feature = "stage") { Some("DEV".to_owned()) } else { None },
            fan_max_speed: Some(DEFAULT_MAX_FAN_SPEED),
            slow_internet_ping_threshold: DEFAULT_SLOW_INTERNET_PING_THRESHOLD,
            block_signup_when_no_internet: DEFAULT_BLOCK_SIGNUPS_WHEN_NO_INTERNET,
            ir_eye_save_fps_override: None,
            ir_face_save_fps_override: None,
            thermal_save_fps_override: None,
            contact_lens_model_config: None,
            fraud_check_engine_config: fraud_check::BackendConfig {},
            ir_net_model_configs: None,
            iris_model_configs: None,
            child_threshold: None,
            face_identifier_model_configs: face_identifier::types::BackendConfig {
                face_identifier_model_configs: None,
            },
            thermal_camera_pairing_status_timeout: DEFAULT_THERMAL_CAMERA_PAIRING_STATUS_TIMEOUT,
            thermal_camera: false,
            depth_camera: false,
            self_serve: false,
            self_serve_button: false,
            self_serve_ask_op_qr_for_possibly_underaged: false,
            self_serve_ask_op_qr_for_possibly_underaged_timeout: QR_SCAN_TIMEOUT,
            self_serve_app_skip_capture_trigger: false,
            // TODO: This is for demo purposes, we should reduce this eventually when the video comes before the QR.
            self_serve_app_capture_trigger_timeout: Duration::from_millis(120_000),
            self_serve_biometric_capture_timeout: DEFAULT_BIOMETRIC_CAPTURE_TIMEOUT_SELF_SERVE,
            mirror_default_phi_offset_degrees: if identification::HARDWARE_VERSION
                .contains("Diamond")
            {
                0.0
            } else {
                -0.46
            },
            mirror_default_theta_offset_degrees: if identification::HARDWARE_VERSION
                .contains("Diamond")
            {
                0.0
            } else {
                -0.35
            },
            process_agent_logger_pruning: !cfg!(feature = "stage"),
            backend_http_request_timeout: Duration::from_millis(60_000 * 3),
            backend_http_connect_timeout: Duration::from_millis(30_000),
            pcp_v3: false,
            pcp_tier1_blocking_threshold: 12,
            pcp_tier1_dropping_threshold: u32::MAX,
            pcp_tier2_blocking_threshold: u32::MAX,
            pcp_tier2_dropping_threshold: 12,
            ignore_user_centric_signups: false,
            user_qr_validation_use_full_operator_qr: false,
```
