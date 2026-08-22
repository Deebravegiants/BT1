### Title
Operator/User QR codes marked as `signup_extension` bypass all backend authentication for both operator and user identity - (File: src/plans/mod.rs, src/plans/qr_scan/user.rs)

### Summary
`ContributionNft::mint` in the external report is exploitable because it trusts an unauthenticated, attacker-controlled parameter (the caller) instead of requiring an authorization check, corrupting downstream state. The direct analog in orb-core is that `verify_operator_qr_code` and `handle_user_qr_code` both skip the backend identity/authorization call entirely whenever a scanned QR code sets the `signup_extension` flag, trusting purely local, unauthenticated regex-parsed text instead. Because this flag and the "mode"/"parameters" fields are attacker-controlled plaintext (no signature or backend round-trip), an unprivileged person presenting a crafted QR code to the orb can walk through the operator-authorization step and the user-authorization step of the signup flow without ever calling the real backend validation endpoints.

### Finding Description
`qr_scan::user::Data::try_parse` parses a QR code string with a local regex (`QR_CODE_SIGNUP_EXTENSION`) and sets `signup_extension = true` plus an attacker-supplied `mode`/`parameters` pair, with no cryptographic signature or backend check involved. [1](#0-0) 

This same `Data` type is reused for the *operator* QR code (`qr_scan::operator::Data::Normal(user::Data)`), and its only gate is that if `signup_extension()` is true, `signup_extension_config` must be `Some` — still just a locally parsed field, not anything backend-verified. [2](#0-1) 

When the orb validates the "operator" QR code, `verify_operator_qr_code` short-circuits and returns a synthetic, always-valid `LocationData` the moment `qr_code.signup_extension()` is true — completely skipping the call to `backend::operator_status::request`, which is the actual authorization check against the backend for a legitimate operator: [3](#0-2) 

Similarly, `handle_user_qr_code` checks `operator_data.qr_code.signup_extension() || user_qr_code.signup_extension()`; if both operator and user QR codes assert this flag, it returns a default, unauthenticated `UserData::default()` and never calls `verify_user_qr_code` (which normally hits `backend::user_status::request`, the equivalent of the missing authorization check in the reported bug): [4](#0-3) 

`backend::user_status::request` is the code path that is bypassed — it is the one that actually verifies the user's identity commitment, decodes backend-issued encryption keys, and verifies `user_data` against a QR-embedded hash: [5](#0-4) 

The resulting attacker-controlled `mode` value is then used, unauthenticated, to select which biometric-capture "extension" plan runs (`PupilContractionExtension`, `FocusSweepExtension`, `MirrorSweepExtension`, `MultiWavelength`, `Overcapture`), directly altering camera/MCU behavior during the capture phase: [6](#0-5) 

This mirrors the reported bug class exactly: a function/flow that is supposed to be authorization-gated (backend-verified operator/user identity, analogous to "only proposal proposer/admin may mint") instead trusts an attacker-suppliable flag/parameter and skips the check, letting an unauthorized actor drive a privileged code path with self-chosen parameters that get consumed downstream (capture configuration, debug report, PCP metadata) without any authenticity guarantee.

However, this path is compiled only behind `#[cfg(feature = "internal-data-acquisition")]` (regex, `from_signup_extension`, and the corresponding branches in `mod.rs`), and is additionally runtime-gated by `self.data_acquisition` in `handle_user_qr_code`. I could not confirm from the available index whether this feature is enabled in the shipped/production `orb-core.efi` build or is restricted to an internal research/data-collection build variant — the index only shows `internal-data-acquisition` referenced across `src/agents/image_notary.rs`, `src/plans/idle.rs`, `src/bin/orb-core.rs`, `src/brokers/orb.rs`, `src/cli.rs`, and `Cargo.toml`, without a definitive statement of whether it is a default/production feature.

### Impact Explanation
If `internal-data-acquisition` is active on any fielded orb, this allows a completely unauthenticated person to:
- Impersonate a valid "operator" and start a signup session without the orb ever contacting the backend to confirm operator authorization/location (`backend::operator_status::request` never invoked).
- Impersonate/inject a "user" signup session using attacker-chosen `mode`/`parameters` without the orb ever contacting the backend user-status endpoint that would normally return the user's real `id_commitment` and backend encryption keys, and without the `user_data.verify(user_data_hash)` check that ties the session to a legitimately-issued app QR code.
- Cause biometric capture to run in an attacker-chosen mode/parameter set (e.g. arbitrary octal wavelength or duration values consumed via `u8::from_str_radix`/`parse_duration`), which is then embedded into the signup debug report / PCP metadata as if it were a normal, backend-authorized data-acquisition signup.

This is a cross-signup / misattributed-signup style issue: state that should only be reachable by a backend-authorized operator/app session becomes reachable by anyone who can print or display two QR codes to the orb's camera, cascading into the same class of impact called out in the reported bug (incorrect/unauthenticated parameters flowing into downstream processing that assumes prior authorization).

### Likelihood Explanation
Exploitation requires only physical presentation of two crafted, non-cryptographic text strings (matching the `QR_CODE_SIGNUP_EXTENSION` regex) to the orb's camera — no credentials, no network access, no privileged keys. The only gating factors are whether `internal-data-acquisition` is compiled into the deployed binary and whether `self.data_acquisition` is enabled at runtime; if both are true in any field-deployed configuration, the bypass is trivially reachable by a normal, unprivileged bystander.

### Recommendation
- Never let `signup_extension` (or its `mode`/`parameters`) skip the backend authorization calls (`backend::operator_status::request` for the operator QR and `backend::user_status::request` for the user QR). At minimum, require that the backend explicitly authorizes data-acquisition/extension sessions (e.g., have the backend return a flag/token permitting the extension mode) rather than trusting a bit embedded in orb-parsed QR text.
- If `internal-data-acquisition` is intended strictly for internal, non-production hardware, ensure it cannot be compiled into or enabled on customer/production-facing orb builds, and add a runtime assertion/kill-switch tied to backend-issued configuration rather than a purely local CLI/feature flag.
- Require the same `user_data_hash`/`verify()` integrity check used for normal QR codes to also apply to `signup_extension` QR codes so extension parameters cannot be forged independently of a backend-issued grant.

### Proof of Concept
1. Attacker generates two text strings matching `QR_CODE_SIGNUP_EXTENSION`'s format (e.g. `userid:<any-id>:1::4:7::` for an "Overcapture" mode with param `7`), one intended as "operator" and one as "user" QR code — no cryptographic material or backend interaction needed, since the regex only requires the literal text pattern shown in `qr_scan/user.rs` tests such as `test_data_acquisition_double_params`. [7](#0-6) 
2. Present the "operator" QR code to the orb; `verify_operator_qr_code` sees `qr_code.signup_extension() == true` and returns a synthetic always-valid `LocationData` without any backend call. [8](#0-7) 
3. Present the "user" QR code; `handle_user_qr_code` sees both operator and user QR are `signup_extension`, extracts the attacker's `mode`, and returns `UserData::default()` without calling `verify_user_qr_code`/the backend. [9](#0-8) 
4. The orb proceeds into `biometric_capture` and dispatches to the attacker-chosen extension plan (e.g. Overcapture) using attacker-supplied wavelength/duration parameters, entirely without backend-verified operator or user identity. [6](#0-5)

### Citations

**File:** src/plans/qr_scan/user.rs (L142-157)
```rust
    #[cfg(feature = "internal-data-acquisition")]
    #[must_use]
    fn from_signup_extension(captures: &Captures) -> Self {
        let v2_data = Self::from_v2(captures);
        let mode = SignupMode::parse(captures.name("mode").map(|mode_group| mode_group.as_str()));
        let parameters = captures
            .name("parameters")
            .map(|parameters_group| parameters_group.as_str().to_string());

        Self {
            user_id: v2_data.user_id,
            signup_extension: true,
            signup_extension_config: mode.map(|mode| SignupExtensionConfig { mode, parameters }),
            user_data_hash: None,
        }
    }
```

**File:** src/plans/qr_scan/user.rs (L301-314)
```rust
        #[test]
        fn test_data_acquisition_double_params() {
            let text = "userid:data_acquisition_mode_overcapture:1::5:7:20500::";
            let data =
                Data::from_signup_extension(&QR_CODE_SIGNUP_EXTENSION.captures(text).unwrap());
            assert_eq!(
                data.signup_extension_config.as_ref().unwrap().mode,
                SignupMode::Overcapture
            );
            assert_eq!(
                data.signup_extension_config.unwrap().parameters,
                Some("7:20500".to_string())
            );
        }
```

**File:** src/plans/qr_scan/operator.rs (L40-48)
```rust
    fn try_parse(code: &str) -> Option<Self> {
        let normal = user::Data::try_parse(code)
            .filter(
                |d| if d.signup_extension() { d.signup_extension_config.is_some() } else { true },
            )
            .map(Data::Normal);
        if normal.is_some() {
            return normal;
        }
```

**File:** src/plans/mod.rs (L1060-1091)
```rust
        if operator_data.qr_code.signup_extension() || user_qr_code.signup_extension() {
            if user_qr_code.signup_extension() && operator_data.qr_code.signup_extension() {
                if let Some(SignupExtensionConfig { mode, parameters: _ }) = user_qr_code
                    .signup_extension_config
                    .as_ref()
                    .or(operator_data.qr_code.signup_extension_config.as_ref())
                {
                    dd_incr!("main.count.data_acquisition.mode", &format!("mode:{mode:?}"));
                    return Ok(Some(Some((
                        user_qr_code,
                        backend::user_status::UserData::default(),
                        user_qr_code_string,
                    ))));
                }
            }
            orb.ui.qr_scan_unexpected(QrScanSchema::User, QrScanUnexpectedReason::Invalid);
            dd_incr!("main.count.data_acquisition.failure.user_qr_code", "type:invalid_qr");
            tracing::error!(
                "Invalid user QR-code format for data acquisition. User QR-code: \
                 {user_qr_code:?}. Operator QR-code: {:?}",
                operator_data.qr_code
            );
            return Ok(None);
        }

        if let Some(user_data) =
            self.verify_user_qr_code(orb, &user_qr_code, operator_data, qr_capture_start).await?
        {
            return Ok(Some(Some((user_qr_code, user_data, user_qr_code_string))));
        }
        Ok(None)
    }
```

**File:** src/plans/mod.rs (L1184-1210)
```rust
        } = if let Some(SignupExtensionConfig { mode, parameters: _ }) =
            &debug_report.signup_extension_config
        {
            match mode {
                qr_scan::user::SignupMode::PupilContractionExtension => {
                    tracing::info!("Pupil Contraction extension: activated");
                    biometric_capture::pupil_contraction::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::FocusSweepExtension => {
                    tracing::info!("Focus Sweep extension: activated");
                    biometric_capture::focus_sweep::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::MirrorSweepExtension => {
                    tracing::info!("Mirror Sweep extension: activated");
                    biometric_capture::mirror_sweep::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::MultiWavelength => {
                    tracing::info!("Multi-wavelength extension: activated");
                    biometric_capture::multi_wavelength::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::Overcapture => {
                    tracing::info!("Overcapture extension: activated");
                    biometric_capture::overcapture::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::Basic => plan.run(orb).await?,
            }
        } else {
```

**File:** src/plans/mod.rs (L1543-1558)
```rust
    /// Checks if `qr_code` is a valid operator QR-code through the backend.
    #[allow(clippy::cast_possible_truncation)]
    async fn verify_operator_qr_code(
        &self,
        orb: &mut Orb,
        qr_code: &qr_scan::user::Data,
        qr_capture_start: Instant,
    ) -> Result<Option<(u64, backend::operator_status::LocationData)>> {
        if qr_code.signup_extension() || self.operator_qr_code_override.is_some() {
            return Ok(Some((0, backend::operator_status::LocationData {
                team_operating_country: "DEV".to_string(),
                session_coordinates: Coordinates { latitude: 0.0f64, longitude: 0.0f64 },
                stationary_location_coordinates: None,
            })));
        }
        let http_start = Instant::now();
```

**File:** src/backend/user_status.rs (L145-179)
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
```
