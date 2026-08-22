### Title
Attacker-controlled `signup_extension` flag in a scanned QR code bypasses backend operator/user identity verification - (File: `src/plans/mod.rs`)

### Summary
`verify_operator_qr_code` and `handle_user_qr_code` both contain an unconditional bypass of backend-side identity verification whenever a scanned QR code reports `signup_extension() == true`. This mirrors the RocketStorage `tx.origin` pattern in the external report: a normally-strict authorization check (`onlyLatestRocketNetworkContract`/backend validation) has a secondary, more permissive branch intended only for a specific trusted operating mode (internal data-acquisition tooling), and that branch is gated on attacker-influenced/self-reported data rather than a robust, unforgeable signal.

### Finding Description
In `verify_operator_qr_code`, the very first check is: [1](#0-0) 

which returns a synthetic, trusted `LocationData` ("DEV" country, 0/0 coordinates) without ever calling the backend `operator_status::request`, if `qr_code.signup_extension()` is true. Similarly `handle_user_qr_code` skips `verify_user_qr_code` (the real backend call) entirely when either the operator or user QR code carries `signup_extension()`: [2](#0-1) 

`signup_extension` is a boolean field parsed straight out of the QR code payload itself: [3](#0-2) 

The only runtime gate that filters this out is compiled in only under the `internal-data-acquisition` feature and only rejects the *user* QR code when `self.data_acquisition` is false: [4](#0-3) 

This gate is `#[cfg(feature = "internal-data-acquisition")]`, so it is compiled out entirely in production builds that don't include that feature, and even when compiled in, it does not filter the **operator** QR code's `signup_extension` flag at all — only `verify_operator_qr_code`'s own inline check (`qr_code.signup_extension() || self.operator_qr_code_override.is_some()`) gates that, and it has no such runtime restriction.

This is analogous to the reported Solidity bug: a trust "switch" (backend verification) is bypassed based on a condition (`signup_extension`) that is not cryptographically bound to a genuinely privileged actor — it is simply a flag embedded in data the orb parses from a QR code presented to the camera, i.e., attacker-reachable input in the signup-authorization trust boundary.

### Impact Explanation
If reachable in a production build (I was unable to fully confirm the exact feature-flag configuration used in shipped production binaries — the `internal-data-acquisition` cfg gate is the only barrier I found, and it does not cover the operator-QR path in `verify_operator_qr_code`), an unprivileged person presenting a crafted QR code with `signup_extension = true` could cause the orb to treat the QR code as a validated operator/user without ever contacting the backend for identity/authorization checks. This could permit an unauthorized signup session to proceed (misattributed/unauthorized signup), since normal operator and user identity verification, which the backend uses to enforce distributor/location/eligibility policy, is skipped.

### Likelihood Explanation
Likelihood is uncertain from static reading alone: the intended purpose of `signup_extension` is internal data-acquisition tooling, and the `#[cfg(feature = "internal-data-acquisition")]` block suggests the authors were aware this needs restricting for the *user* QR code path — but that restriction (a) is compiled out unless that feature is present and (b) does not apply to `verify_operator_qr_code`'s independent bypass. Whether the shipped/production Cargo feature set excludes `internal-data-acquisition` (which would leave the operator-QR bypass with zero runtime restriction) could not be verified with the tools available.

### Recommendation
- Do not gate any backend-verification bypass on data embedded in the QR code content itself. Any "internal test/data-acquisition" bypass path should require a build-time feature (already the pattern for `data_acquisition`) rather than relying on a QR-embedded boolean, and this restriction must be applied uniformly to both `verify_operator_qr_code` and `handle_user_qr_code`.
- Document explicitly, in code comments near `verify_operator_qr_code`, why `qr_code.signup_extension()` alone is trusted to skip backend calls, and confirm/enforce that this path is unreachable in production builds (e.g., via a compile-time assertion or `debug_assert!`/`cfg` guard tied to `internal-data-acquisition`, not runtime-only checks).
- Consider requiring the `operator_qr_code_override`/`signup_extension` bypass to also require an explicit `data_acquisition` runtime flag, matching the existing gate on the user-QR path, so the two code paths are consistent.

### Proof of Concept
Not independently verified end-to-end (would require confirming production Cargo feature flags and the QR MECARD/user-data parser's acceptance of `signup_extension` in the shipped configuration). Based on the code:
1. Craft a user (or operator) QR code payload that `qr_scan::user::Data::try_parse` decodes with `signup_extension = true`.
2. Present it during the operator/user QR scan phase of `MasterPlan::do_signup`.
3. `verify_operator_qr_code` (or `handle_user_qr_code`) short-circuits, returning a synthetic "valid" result without ever calling `backend::operator_status::request` / `backend::user_status::request`, i.e., no backend authorization check occurs for that session.

### Citations

**File:** src/plans/mod.rs (L1011-1028)
```rust
    #[cfg_attr(not(feature = "internal-data-acquisition"), allow(unused_mut))]
    async fn handle_user_qr_code(
        &self,
        mut scan_result: Result<(qr_scan::user::Data, String), qr_scan::ScanError>,
        orb: &mut Orb,
        operator_data: &OperatorData,
        qr_capture_start: Option<Instant>,
    ) -> Result<Option<Option<(qr_scan::user::Data, backend::user_status::UserData, String)>>> {
        #[cfg(feature = "internal-data-acquisition")]
        if !self.data_acquisition {
            scan_result = scan_result.and_then(|(data, string)| {
                if data.signup_extension {
                    Err(qr_scan::ScanError::Invalid)
                } else {
                    Ok((data, string))
                }
            });
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

**File:** src/plans/mod.rs (L1550-1557)
```rust
    ) -> Result<Option<(u64, backend::operator_status::LocationData)>> {
        if qr_code.signup_extension() || self.operator_qr_code_override.is_some() {
            return Ok(Some((0, backend::operator_status::LocationData {
                team_operating_country: "DEV".to_string(),
                session_coordinates: Coordinates { latitude: 0.0f64, longitude: 0.0f64 },
                stationary_location_coordinates: None,
            })));
        }
```

**File:** src/plans/qr_scan/user.rs (L71-82)
```rust
/// User QR-code data.
#[derive(Default, Clone, Debug)]
pub struct Data {
    /// User ID in format of 128-bit UUIDv4.
    pub user_id: String,
    /// It's a data acquisition QR code.
    pub signup_extension: bool,
    /// Data acquisition configuration.
    pub signup_extension_config: Option<SignupExtensionConfig>,
    /// Hash of the user data stored in the backend.
    pub user_data_hash: Option<Vec<u8>>,
}
```
