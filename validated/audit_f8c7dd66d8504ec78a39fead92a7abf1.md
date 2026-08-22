### Title
Operator QR-code identity verification is unconditionally bypassed when `signup_extension` flag is set - ([File: src/plans/mod.rs])

### Summary
`verify_operator_qr_code` is the function responsible for validating an operator's identity/location against the backend before a signup is allowed to proceed. It contains a bypass condition analogous to the `Funds.maxFundDur`/`maxLoanDur` bug pattern: a secondary condition (`qr_code.signup_extension()`) causes the entire backend verification check to be skipped, returning a synthetic "valid" result instead of actually validating anything against the backend.

### Finding Description
In `verify_operator_qr_code`, the code short-circuits the actual backend verification of the operator QR-code: [1](#0-0) 

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

This mirrors the reported bug class exactly: the function is supposed to always check the operator identity/location against the backend (analogous to always checking `maxFundDur`), but as soon as `qr_code.signup_extension()` evaluates true, that check is entirely skipped and a hardcoded "valid" location/result is substituted (analogous to skipping the `maxFundDur` check when `maxLoanDur` is set).

The `signup_extension()` flag is derived from data embedded in the scanned QR-code payload itself (`qr_scan::user::Data`), which is attacker/user-controllable content presented to the camera during the "operator QR-code scanning" phase — this is not a trusted, orb-local flag. If `signup_extension()` can be set to `true` by crafting the QR-code content scanned during the operator step, the orb will treat any presented QR-code as a fully verified operator, bypassing the real backend identity check (`backend::operator_status::request`).

### Impact Explanation
If reachable with an unprivileged, attacker-crafted QR code, this allows an attacker to impersonate a valid operator without any backend verification of operator identity or location, since the function returns a synthetic "valid" result (`team_operating_country: "DEV"`, coordinates `0.0, 0.0`) instead of performing the actual check. This directly leads to unauthorized/misattributed signup flows, since the caller (`scan_remaining_qr_codes`/`scan_initial_qr_codes`) treats the return value as authoritative proof that the operator was verified before proceeding into biometric capture and enrollment.

### Likelihood Explanation
Likelihood is uncertain and could not be fully confirmed given tool/iteration limits. The second disjunct, `self.operator_qr_code_override.is_some()`, is only reachable via a CLI override intended for internal testing (gated behind the `allow-plan-mods` feature per other code in this file), which would be a test-only path and excluded per the rules. The first disjunct, `qr_code.signup_extension()`, is defined in `src/plans/qr_scan/user.rs`, but I was unable to load that file's contents in this session (tool call failed due to a missing parameter, and no further iterations were available) to confirm: (1) whether `signup_extension()` is parsed from arbitrary/unprivileged QR-code content or is otherwise gated by a feature flag / internal-only code path (the codebase context elsewhere strongly suggests `signup_extension` correlates with `SignupMode`/`internal-data-acquisition` feature and CLI-only "data acquisition" test flows), and (2) whether this bypass is reachable in production builds. Given the surrounding code explicitly gates similar `signup_extension` checks behind `#[cfg(feature = "internal-data-acquisition")]` (see the `if !self.data_acquisition { ... signup_extension ... }` block in `scan_operator_qr_code`), it is plausible that this bypass is also confined to an internal testing/data-acquisition feature path rather than being reachable by a general unprivileged user in production.

### Recommendation
Confirm whether `qr_code.signup_extension()` can be set to `true` through content parsed from a normal (non-test, non-CLI-override) QR-code scan in a production build. If so, the backend operator verification (`backend::operator_status::request`) must not be bypassed for that flag alone in production code paths — the check should either be feature-gated identically to the `internal-data-acquisition` path already used elsewhere in `scan_operator_qr_code`, or removed from the production bypass condition entirely, consistent with never skipping identity verification checks based on user-supplied data.

### Proof of Concept
Not established with certainty. A conclusive PoC would require confirming, via `src/plans/qr_scan/user.rs`, exactly how `signup_extension()` is derived and whether it's reachable from an arbitrary QR-code string scanned in the "operator QR-code scanning" phase in a production (non-test-feature) build. This could not be completed within the available tool budget.

### Citations

**File:** src/plans/mod.rs (L1543-1557)
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
```
