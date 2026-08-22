### Title
Operator QR-code validation is fully bypassed when `operator_qr_code_override` is set - ([File: src/plans/mod.rs])

### Summary
`verify_operator_qr_code` unconditionally skips the backend operator authorization check and returns a synthetic "valid" location result whenever `self.operator_qr_code_override.is_some()`, mirroring the reported bug class: a value/flag intended only for a restricted testing path silently disables a core protection (there, the 100-day IL protection window; here, operator QR authenticity/authorization verification).

### Finding Description
`verify_operator_qr_code` is the function responsible for calling the backend to confirm an operator QR code is valid before a signup is allowed to proceed: [1](#0-0) 

The very first branch of the function is:
```rust
if qr_code.signup_extension() || self.operator_qr_code_override.is_some() {
    return Ok(Some((0, backend::operator_status::LocationData {
        team_operating_country: "DEV".to_string(),
        session_coordinates: Coordinates { latitude: 0.0f64, longitude: 0.0f64 },
        stationary_location_coordinates: None,
    })));
}
``` [2](#0-1) 

This means that as soon as `operator_qr_code_override` is set on the signup `Plan`, the code never calls `backend::operator_status::request(qr_code)` and instead fabricates a "valid" operator location response with hardcoded `"DEV"` country/city data and `(0.0, 0.0)` coordinates — exactly analogous to the report's incorrectly-initialized `timeForFullProtection` short-circuiting the intended 100-day protection logic. This override is consumed from `do_signup`/`scan_remaining_qr_codes` via `operator_qr_expiration_time` and `self.operator_qr_code_override`, and is used to skip normal operator-QR verification entirely rather than only under an isolated, compiled-out test harness.

The critical open question — which the index could not resolve — is exactly how and where `operator_qr_code_override` is populated (e.g., whether it's gated behind a `#[cfg(test)]`/feature flag, a CLI/dev-only argument, or a field that can be reached through a production code path such as internal-data-acquisition tooling). All 7 references to `operator_qr_code_override` are confined to `src/plans/mod.rs`; I was not able to fully trace its construction site(s) or feature gating within the available iterations.

### Impact Explanation
If `operator_qr_code_override` is reachable outside of an explicitly test-only/dev-only compiled path, an operator QR code (and by extension the signup session's location/authorization binding) could be accepted without ever being validated by the backend, allowing an unauthorized or spoofed operator context to be attached to a signup — a direct signup-authorization bypass in the same spirit as the referenced report (a protection mechanism silently disabled due to a leftover override).

### Likelihood Explanation
Likelihood cannot be confirmed as concrete without locating the exact call sites that set `operator_qr_code_override` and their compilation/feature gating. Since the task rules require rejecting "test-only paths" and I could not verify from the index whether this override is strictly limited to a non-production test harness or is reachable in shipped builds, I cannot assert with confidence that this is exploitable in production as-is.

### Recommendation
Not applicable without further confirmation of reachability; if pursued, verify (via the actual repo, not just the index) all sites constructing `Plan.operator_qr_code_override`, confirm whether it is behind `#[cfg(test)]`/a feature flag excluded from production builds, and if it is reachable in production, gate it so it can never bypass `backend::operator_status::request` outside of test binaries.

### Proof of Concept
Not constructible from the index alone — a full PoC requires confirming the construction/gating of `operator_qr_code_override`, which was not fully retrievable within the available search iterations.

Given the significant unresolved uncertainty about whether `operator_qr_code_override` is a genuine production-reachable bypass or a test-only construct (which the task rules explicitly instruct to reject), and given the index's size limits prevented full tracing of every reference to this field, I recommend starting a Devin session with full repository access to confirm this before treating it as a validated finding.

### Citations

**File:** src/plans/mod.rs (L1543-1578)
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
        match backend::operator_status::request(qr_code).await {
            Ok(backend::operator_status::Status { valid: true, location_data, reason: _ }) => {
                let location_data = location_data
                    .expect("to always have a result from the backend if valid == true");
                orb.ui.qr_scan_success(QrScanSchema::Operator);
                dd_incr!("main.count.global.distr_code_validated");
                tracing::info!("Operator QR-code validated: {qr_code:?}");
                dd_timing!("main.time.signup.distr_qr_code_capture", qr_capture_start);
                return Ok(Some((http_start.elapsed().as_millis() as u64, location_data)));
            }
            Ok(backend::operator_status::Status { valid: false, .. }) => {
                orb.ui.qr_scan_fail(QrScanSchema::Operator);
                dd_incr!("main.count.signup.result.failure.distr_qr_code", "type:invalid_qr");
            }
            Err(_) => {
                orb.ui.qr_scan_fail(QrScanSchema::Operator);
            }
        }
        Ok(None)
    }
```
