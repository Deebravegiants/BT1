### Title
Config-only Age-Verification Gate Never Enforced in Self-Serve Signup Flow - (File: src/config.rs, src/plans/mod.rs)

### Summary
Both `child_threshold` (the person-classifier / under-age detection threshold) and `self_serve_ask_op_qr_for_possibly_underaged` (the flag meant to require an operator QR-code scan when a possibly under-age person is detected in self-serve mode) exist only as configuration fields. [1](#0-0)  Neither identifier is referenced anywhere in the signup/enrollment control flow (`src/plans/mod.rs`, `biometric_capture`, `biometric_pipeline`), only in `src/config.rs` and `src/backend/config.rs` where they are parsed from the backend response. [2](#0-1)  This mirrors the M-22 bug class: a safety threshold that is supposed to gate a sensitive state transition (minimum collateral before allowing borrow/withdraw; here, mandatory operator re-verification before allowing a possibly-underage self-serve signup to proceed) is defined but not actually wired into the code path that performs the state-changing action, so the check can never fire.

### Finding Description
The `Config` struct documents the intended control precisely: *"Ask the operator for a QR code when a possibly underaged person is detected"* in self-serve mode, with an associated timeout. [3](#0-2)  This is populated from backend config the same way as every other operational toggle. [4](#0-3)  A default value (`false`) and default timeout are set in `Default for Config`. [5](#0-4) 

However, the self-serve signup path (`idle_wait_for_signup_request`, `idle_scan_user_qr_code`, `do_signup`) never reads `self_serve_ask_op_qr_for_possibly_underaged`, never calls into an age-detection routine, and never conditionally requests the operator to re-scan a QR-code. [6](#0-5)  The self-serve idle path only branches on `self_serve` / `self_serve_button` to decide whether to scan the user QR-code directly or wait for a button press — there is no branch that consults age-verification state before proceeding into `do_signup`, which subsequently performs the full biometric capture, pipeline, and enrollment. [7](#0-6)  The `orb-relay-client` crate does define a message type `AgeVerificationRequiredFromOperator`, showing the intended wire protocol for this feature exists, but no producer of this message was found anywhere in `orb-core`'s signup plans. [8](#0-7) 

Likewise `child_threshold` (person-classifier under-age score threshold) is only present in the config structs and is never consumed by `biometric_pipeline` or `enroll_user` in the indexed code, meaning even the underlying under-age *detection* signal that would need to drive this control is not observably connected to enrollment decisions. [9](#0-8) 

The root cause is structurally identical to M-22: the enforcement point (operator age re-verification / minimum threshold) is decoupled from the state-changing action it is meant to gate (self-serve enrollment / collateral withdrawal), so an entity can reach the sensitive state (full enrollment) without ever passing through the intended check.

### Impact Explanation
If this control is genuinely unwired (which is what the available index shows), a self-serve Orb configured with `self_serve = true` and `self_serve_ask_op_qr_for_possibly_underaged = true` provides no actual technical enforcement preventing a possibly-underage individual from completing signup and biometric enrollment without an operator present to re-verify age. This is a misattributed/unauthorized signup impact category: an enrollment is created and biometric data (iris/face) is captured and uploaded via the PCP pipeline for a person who should have been blocked pending operator verification. [10](#0-9) 

### Likelihood Explanation
Likelihood is moderate to low-confidence given index limitations: the `codebase_search`/`grep_search` tools show no call sites for `self_serve_ask_op_qr_for_possibly_underaged` or `child_threshold` outside the two config files, across the entire indexed repository. This strongly suggests the feature is either fully unimplemented in this build, or its implementation lives in a component/module not covered by the current index (e.g., a python agent or a private extension not present in this snapshot). Given this repo's FOSS nature already shows other checks stripped out (`detect_fraud` explicitly says "WE HAVE DELETED ALL FRAUD CHECKS" and unconditionally returns `Ok(false)`) [11](#0-10) , it is plausible the age-verification gate was similarly removed/never ported, making the self-serve path silently permissive rather than fail-safe.

### Recommendation
- Wire `self_serve_ask_op_qr_for_possibly_underaged` into the self-serve idle/signup flow (`idle_wait_for_signup_request` / `do_signup`) so that when an under-age signal is raised (via `child_threshold` from the person-classifier), the flow blocks progression to biometric capture/enrollment and instead sends `self_serve::orb::v1::AgeVerificationRequiredFromOperator` over `orb_relay`, waiting up to `self_serve_ask_op_qr_for_possibly_underaged_timeout` for an operator QR-code scan before continuing.
- Add an explicit fail-closed default: if age-detection or the operator-verification round trip cannot complete, abort the signup rather than silently continuing (mirroring `fraud_checks_strict`'s "if fraud data are missing, assume fraud is detected" pattern already used elsewhere). [12](#0-11) 
- Add integration tests asserting that a simulated under-age classification in self-serve mode never reaches `enroll_user` without a successful operator QR-code verification step.

### Proof of Concept
1. Configure an Orb in self-serve mode: `self_serve = true`, `self_serve_button = false`, `self_serve_ask_op_qr_for_possibly_underaged = true`. [13](#0-12) 
2. A user scans their own QR-code via `idle_scan_user_qr_code`, which only checks `check_signup_conditions` (internet status) and QR-code validity — no age classification gate exists in this path. [14](#0-13) 
3. `do_signup` proceeds directly through `biometric_capture` → `biometric_pipeline` → `enroll_user`, with no call site consulting `self_serve_ask_op_qr_for_possibly_underaged` or `child_threshold` to interrupt the flow and request operator verification. [15](#0-14) 
4. Enrollment completes and biometric data is uploaded, without the operator-verification step ever having a functional trigger point in the codebase.

**Uncertainty note:** Due to index size limits, it is possible the actual enforcement logic for age detection/operator re-verification lives in a file or module not surfaced by the available search tools (e.g., a private/vendor extension). I could not find any call site for `self_serve_ask_op_qr_for_possibly_underaged` or `child_threshold` beyond the config definitions, but I cannot rule out with full certainty that such logic exists elsewhere outside the indexed content. Starting a full Devin session with complete repository access would allow verifying whether this gate is truly unimplemented or simply not indexed.

### Citations

**File:** src/config.rs (L75-93)
```rust
    /// Person Classifier config: under-age threshold.
    pub child_threshold: Option<f32>,
    /// Face Identifier: Namespaced Face Identifier configs collection.
    pub face_identifier_model_configs: face_identifier::types::BackendConfig,
    /// How long the thermal camera agent will wait until it assumes
    /// the cam is stuck pairing.
    pub thermal_camera_pairing_status_timeout: Duration,
    /// Whether the thermal camera agent is enabled or not.
    pub thermal_camera: bool,
    /// Whether the depth camera agent is enabled or not.
    pub depth_camera: bool,
    /// Self-serve mode.
    pub self_serve: bool,
    /// Alternative mode for self-serve: start a signup with a button press.
    pub self_serve_button: bool,
    /// Ask the operator for a QR code when a possibly underaged person is detected.
    pub self_serve_ask_op_qr_for_possibly_underaged: bool,
    /// How long to wait for the operator to scan the QR code when a possibly underaged person is detected.
    pub self_serve_ask_op_qr_for_possibly_underaged_timeout: Duration,
```

**File:** src/config.rs (L230-239)
```rust
            self_serve: self_serve.unwrap_or(default.self_serve),
            self_serve_button: self_serve_button.unwrap_or(default.self_serve_button),
            self_serve_ask_op_qr_for_possibly_underaged:
                self_serve_ask_op_qr_for_possibly_underaged
                    .unwrap_or(default.self_serve_ask_op_qr_for_possibly_underaged),
            self_serve_ask_op_qr_for_possibly_underaged_timeout:
                self_serve_ask_op_qr_for_possibly_underaged_timeout.map_or(
                    default.self_serve_ask_op_qr_for_possibly_underaged_timeout,
                    Duration::from_millis,
                ),
```

**File:** src/config.rs (L406-409)
```rust
            self_serve: false,
            self_serve_button: false,
            self_serve_ask_op_qr_for_possibly_underaged: false,
            self_serve_ask_op_qr_for_possibly_underaged_timeout: QR_SCAN_TIMEOUT,
```

**File:** src/backend/config.rs (L50-53)
```rust
    pub self_serve: Option<bool>,
    pub self_serve_button: Option<bool>,
    pub self_serve_ask_op_qr_for_possibly_underaged: Option<bool>,
    pub self_serve_ask_op_qr_for_possibly_underaged_timeout: Option<u64>,
```

**File:** src/plans/mod.rs (L394-436)
```rust
    async fn idle_wait_for_signup_request(
        &mut self,
        orb: &mut Orb,
        qr_codes: &QrCodes,
        self_serve: bool,
        self_serve_button: bool,
        operator_qr_expiration_time: Duration,
    ) -> Result<Option<QrCodes>> {
        // We currently support 4 scenarios:
        // 1. Internal testing with a biometric input file.
        // 2. Self-serve mode that always scans for a user QR code.
        // 3. Self-serve mode that expects a button press to ask for a user QR code.
        // 4. Normal mode that expects a button press to ask for an operator QR code and then a user QR code.
        //
        // Scenarios 3 and 4 are handled by the same code path in the following last else-statement.
        let ui_idle_delay = self.ui_idle_delay.take();
        let qr_codes = if self.oneshot || self.has_biometric_input() {
            qr_codes.clone()
        } else if self_serve && !self_serve_button {
            orb.set_phase("User QR-code idle scanning").await;
            let QrCodes::Operator { operator_data } = &qr_codes else {
                panic!("operator QR code needs to be scanned beforehand in self-serve mode");
            };
            let Some((user_qr_code, user_data, user_qr_code_string)) = self
                .idle_scan_user_qr_code(
                    orb,
                    operator_data,
                    operator_qr_expiration_time,
                    ui_idle_delay,
                )
                .await?
            else {
                return Ok(None);
            };
            qr_codes.with_user_qr_code(user_qr_code, user_data, user_qr_code_string)
        } else {
            orb.set_phase("Idle waiting for button press").await;
            self.idle_wait_for_button_press(orb, ui_idle_delay).await?;
            orb.ui.signup_start_operator();
            qr_codes.clone()
        };
        Ok(Some(qr_codes))
    }
```

**File:** src/plans/mod.rs (L456-488)
```rust
    async fn idle_scan_user_qr_code(
        &mut self,
        orb: &mut Orb,
        operator_data: &OperatorData,
        operator_qr_expiration_time: Duration,
        mut ui_idle_delay: Option<time::Sleep>,
    ) -> Result<Option<(qr_scan::user::Data, backend::user_status::UserData, String)>> {
        loop {
            orb.reset_rgb_camera().await?;
            match idle::Plan::with_user_qr_scan(
                ui_idle_delay.take(),
                Some(operator_qr_expiration_time.saturating_sub(operator_data.timestamp.elapsed())),
                #[cfg(feature = "internal-data-acquisition")]
                self.data_acquisition,
            )
            .run(orb)
            .await?
            {
                idle::Value::UserQrCode(qr_scan_result) => {
                    if !check_signup_conditions(orb).await? {
                        continue;
                    }
                    if let Some(Some((user_qr_code, user_data, user_qr_code_string))) =
                        self.handle_user_qr_code(qr_scan_result, orb, operator_data, None).await?
                    {
                        break Ok(Some((user_qr_code, user_data, user_qr_code_string)));
                    }
                }
                idle::Value::TimedOut => break Ok(None),
                idle::Value::ButtonPress => unreachable!(),
            }
        }
    }
```

**File:** src/plans/mod.rs (L490-663)
```rust
    #[allow(clippy::too_many_lines)]
    async fn do_signup(
        &mut self,
        orb: &mut Orb,
        qr_codes: QrCodes,
        dbus: Option<&zbus::SignalContext<'_>>,
    ) -> Result<SignupResult> {
        let Config {
            self_serve,
            pcp_v3,
            orb_relay_announce_orb_id_retries,
            orb_relay_announce_orb_id_timeout,
            orb_relay_shutdown_wait_for_pending_messages,
            orb_relay_shutdown_wait_for_shutdown,
            operator_qr_expiration_time,
            ..
        } = *orb.config.lock().await;
        let mut result = self.start_signup(orb, dbus).await?;
        let Some(qr_codes) =
            self.scan_remaining_qr_codes(orb, qr_codes, operator_qr_expiration_time).await?
        else {
            return Ok(result);
        };
        let debug_report = result.debug_report.insert(DebugReport::builder(
            result.capture_start,
            &result.signup_id,
            &qr_codes,
            orb.config.lock().await.clone(),
        ));

        if !self.is_orb_os_version_allowed(debug_report).await {
            #[cfg(feature = "stage")]
            notify_failed_signup(orb, Some(SignupFailReason::SoftwareVersionBlocked));
            #[cfg(not(feature = "stage"))]
            return Ok(result);
        }

        if self_serve && qr_codes.user_data.orb_relay_app_id.is_none() {
            tracing::error!("Self-serve: orb_relay_app_id is missing in the user data");
            debug_report.signup_app_incompatible_failure();
            return Ok(result);
        }
        if let Some(orb_relay_app_id) = &qr_codes.user_data.orb_relay_app_id {
            if let Err(e) = orb_relay_announce_orb_id(
                orb,
                orb_relay_app_id.clone(),
                self_serve,
                orb_relay_announce_orb_id_retries,
                orb_relay_announce_orb_id_timeout,
                orb_relay_shutdown_wait_for_pending_messages,
                orb_relay_shutdown_wait_for_shutdown,
            )
            .await
            {
                tracing::error!("{e}");
                debug_report.signup_orb_relay_failure();
                return Ok(result);
            }
        }

        // wait for the sound to finish and user to get ready before starting the capture
        sleep(Duration::from_millis(3000)).await;

        let capture = self.biometric_capture(orb, debug_report).await?;
        self.after_biometric_capture(orb, debug_report, capture.is_some(), self_serve).await?;
        let Some(capture) = capture else {
            return Ok(result);
        };
        if self.skip_pipeline() || debug_report.signup_extension_config.is_some() {
            result.success = true;
            return Ok(result);
        }
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
        let user_id = qr_codes.user_qr_code.user_id.clone();
        let user_centric_signup = qr_codes.user_data.user_centric_signup;
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

**File:** src/plans/mod.rs (L1392-1406)
```rust
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

**File:** orb-relay-client/src/lib.rs (L73-80)
```rust
impl IntoPayload for self_serve::orb::v1::AgeVerificationRequiredFromOperator {
    fn into_payload(self) -> Any {
        Any::from_msg(&self_serve::orb::v1::W {
            w: Some(self_serve::orb::v1::w::W::AgeVerificationRequiredFromOperator(self)),
        })
        .unwrap()
    }
}
```

**File:** src/plans/fraud_check.rs (L71-74)
```rust
    /// If fraud data are missing, we assume fraud is detected.
    fn fraud_checks_strict(&self) -> [bool; N_FRAUD_CHECKS] {
        self.fraud_checks().map(|v| v.unwrap_or(true))
    }
```
