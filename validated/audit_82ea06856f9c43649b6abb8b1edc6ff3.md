### Title
Operator QR-code authentication bypass via self-declared `signup_extension` flag - (File: src/plans/mod.rs)

### Summary
The reported GammaProtocol bug is a class of "unvalidated identity/asset accepted from the caller" vulnerability: the `Controller._redeem` function trusted a caller-supplied oToken address instead of verifying it against a real, backend-registered token, letting an attacker fabricate a fake asset and drain real collateral. The closest reachable analog in orb-core is in the operator QR-code verification path, where a caller-controlled flag on the *scanned QR-code data itself* (`signup_extension`) causes the Controller-equivalent function to skip backend authentication entirely and short-circuit to a hardcoded "valid" result, instead of validating the operator identity against the real backend record.

### Finding Description
`verify_operator_qr_code` in `src/plans/mod.rs` is the function responsible for authenticating an operator/distributor QR-code against the backend before an operator is allowed to initiate a signup session: [1](#0-0) 

```rust
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
    match backend::operator_status::request(qr_code).await {
    ...
```

`qr_code.signup_extension()` is a boolean parsed directly out of the physically-scanned QR-code string, via the `QR_CODE_SIGNUP_EXTENSION` regex in `src/plans/qr_scan/user.rs`, which is fully attacker-controlled (anyone can print/display a QR code): [2](#0-1) 

If that flag is set to true in the scanned code, the entire backend call to `backend::operator_status::request(qr_code)` — the function that actually asks the backend "is this a real, registered operator/distributor?" — is skipped. The code instead unconditionally returns `Some(...)` with a dummy `LocationData` and no verification whatsoever, exactly mirroring the GammaProtocol pattern where `_redeem` skipped verifying the token's authenticity and trusted attacker-supplied data.

Compare this with the legitimate path, `backend::operator_status::request`, which does perform real validation against the backend and only returns a valid status if the backend confirms the operator/distributor ID: [3](#0-2) 

The bypass path is gated on the `internal-data-acquisition` cargo feature at the regex-definition site (`#[cfg(any(feature = "internal-data-acquisition", test))]`), but the *branch that skips the backend check* in `verify_operator_qr_code` itself is **not** feature-gated — it unconditionally checks `qr_code.signup_extension()`. This means the security-relevant bypass logic in `Controller`-equivalent code exists in the always-compiled path, contingent only on whether `signup_extension` can ever end up `true`, which depends on whether `internal-data-acquisition` is compiled into the shipped binary. I was not able to conclusively determine, within the available tool budget, whether `internal-data-acquisition` is enabled in production release builds (I found matches in `Cargo.toml` but could not read the file contents before running out of iterations), so I cannot confirm this is reachable in the shipped firmware without further investigation.

### Impact Explanation
If `internal-data-acquisition` is compiled into a production Orb build, an unprivileged party who can present a specially-crafted operator/distributor QR code (matching the `QR_CODE_SIGNUP_EXTENSION` pattern) can make the Orb treat any operator QR-code as validated, without any backend-side confirmation that the operator/distributor is real, authorized, or associated with the correct location/country. This is an authorization bypass for the signup flow's identity-binding stage (Orb operator authentication precedes and gates biometric capture and signup), directly analogous to the "accept attacker-supplied identity and pay out based on it" pattern in the original report. It does not itself leak biometric data, but it removes the operator-authenticity control gating who can initiate signups on the device, and feeds unvalidated location data (`team_operating_country: "DEV"`, lat/long `0.0`) downstream into the signup pipeline.

### Likelihood Explanation
Exploitability depends entirely on whether `internal-data-acquisition` (a feature intended for internal/lab data collection) is enabled in the fielded production binary. If it is disabled in production, `signup_extension` can never be true and this path is dead code, making the bug not reachable by an unprivileged field attacker. I could not verify feature-flag configuration for production builds in the time available — this needs a background agent to check `Cargo.toml` feature defaults, build scripts, and any CI/release-profile configuration.

### Recommendation
- Verify whether `internal-data-acquisition` is enabled in shipped/production builds; if so, gate the entire bypass branch (`qr_code.signup_extension() || ...`) behind `#[cfg(feature = "internal-data-acquisition")]` so it cannot exist in production binaries.
- Even for internal/lab builds, avoid trusting a caller-supplied flag embedded in QR-code data to skip backend authentication; require a separate signed/backend-issued indicator (e.g., a backend flag returned after validating the scanned ID) rather than trusting the raw QR-code payload's self-declared `signup_extension` bit.
- Apply the same scrutiny to `self.operator_qr_code_override`, ensuring it can only be set via a trusted local CLI/config path never reachable from network or QR-code input.

### Proof of Concept
1. Ensure a build with `internal-data-acquisition` feature enabled (if such builds are ever deployed to field units).
2. Craft a QR-code string matching `QR_CODE_SIGNUP_EXTENSION` format, e.g. `userid:<any-id>:1::<mode>::`, so `Data::try_parse` yields `signup_extension = true` (see `src/plans/qr_scan/user.rs:118-121,142-157`).
3. Present this QR code to the Orb as the "operator" QR-code during the scan-operator step.
4. Observe that `verify_operator_qr_code` (`src/plans/mod.rs:1551-1557`) returns `Ok(Some(...))` immediately, with no call to `backend::operator_status::request`, granting operator validation without any backend authorization check.

### Citations

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

**File:** src/plans/qr_scan/user.rs (L106-123)
```rust
    fn try_parse(code: &str) -> Option<Self> {
        if let Ok((user_id, user_data_hash)) = decode_qr(code) {
            return Some(Self {
                user_id: user_id.hyphenated().to_string(),
                signup_extension: false,
                signup_extension_config: None,
                user_data_hash: Some(user_data_hash),
            });
        }
        if let Some(captures) = QR_CODE_V2.captures(code) {
            return Some(Data::from_v2(&captures));
        }
        #[cfg(feature = "internal-data-acquisition")]
        if let Some(captures) = QR_CODE_SIGNUP_EXTENSION.captures(code) {
            return Some(Data::from_signup_extension(&captures));
        }
        None
    }
```

**File:** src/backend/operator_status.rs (L45-76)
```rust
/// Makes a validation request.
pub async fn request(qr_code: &qr_scan::user::Data) -> Result<Status> {
    let request = super::client()?
        .get(format!(
            "{}/api/v1/distributor/{}/orb/{}/status",
            *SIGNUP_BACKEND_URL, qr_code.user_id, *ORB_ID
        ))
        .basic_auth(&*ORB_ID, Some(get_orb_token()?));
    let status: Status = match request.send().await?.error_for_status() {
        Ok(response) => response.json().await?,
        Err(err) => {
            tracing::error!("Received error response {err:?}");
            return Err(err.into());
        }
    };
    if !status.valid {
        tracing::info!(
            "Operator QR-code invalid: {qr_code:?}, reason: {:?}",
            status.reason.as_deref().unwrap_or("<empty>")
        );
        return Ok(status);
    }
    if status.location_data.is_none() {
        tracing::error!("Operator location data are missing");
        return Ok(Status {
            valid: false,
            location_data: None,
            reason: Some("Operator location data are missing".to_string()),
        });
    }
    Ok(status)
}
```
