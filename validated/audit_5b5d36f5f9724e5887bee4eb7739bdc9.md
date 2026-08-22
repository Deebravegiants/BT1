### Title
Stale operator/user QR validation reused across signup lifecycle without re-verification, enabling unauthorized/misattributed signup ([File: src/plans/mod.rs])

### Summary
The Cabal report describes a bug class where a value (claimable share) is fixed at *request* time and blindly trusted at *execution* time, even though the underlying authoritative state (pool value) may have changed in between — leading to unauthorized/unfair outcomes. `orb-core` has a structurally analogous pattern in `scan_remaining_qr_codes` / `idle_scan_user_qr_code` in `src/plans/mod.rs`: the operator/user QR validation result (`user_data: backend::user_status::UserData`, `operator_data`) obtained from a one-time backend call is cached and reused for the remainder of the signup — including through the entire biometric capture and pipeline — as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, a window that defaults to **23 hours** (`Duration::from_secs(60 * 60 * 23)` in `src/config.rs:443`).

### Finding Description
In `src/plans/mod.rs`, `scan_remaining_qr_codes` (lines 788–869) decides whether to reuse previously scanned/validated operator+user QR data or re-scan/re-validate, based solely on an elapsed-time check against `operator_qr_expiration_time`: [1](#0-0) 

If the cached `QrCodes::Both { operator_data, user_qr_code, user_data, .. }` is still "fresh" per this timer, the previously fetched `user_data` (which encodes the backend's authorization decision — validity, `user_centric_signup`, PCP/session keys, etc., from `backend::user_status::request`, see `src/backend/user_status.rs:145-271`) is trusted directly, with **no re-call to the backend** to confirm the user/session/operator is still authorized: [2](#0-1) 

The equivalent applies to the self-serve idle path, `idle_scan_user_qr_code` (lines 456–488), which similarly performs `verify_user_qr_code` (a single backend round trip) once, and the resulting `user_data`/`operator_data` tuple is carried forward through `idle_wait_for_signup_request` (lines 394–436) into `do_signup`, driving the entire capture → pipeline → enrollment sequence (lines 490 onward) without any second validity check against the backend prior to the final `signup_post::request` in `src/backend/signup_post.rs:98-161`.

This mirrors the Cabal root cause precisely: an authorization/eligibility decision is computed once ("at request time") from backend state, cached into a local struct, and then blindly consumed much later ("at execution time") to drive high-impact actions (biometric enrollment), instead of being re-derived from the current backend state immediately before the irreversible action (`enroll_user::Plan::run` → `signup_post::request`).

### Impact Explanation
If the backend's session/user state changes during the up-to-23-hour reuse window (e.g., the operator/session is revoked, the user's authorization expires, the session is superseded, or an attacker replays/holds a previously-scanned QR pairing), `orb-core` will still proceed to run a full biometric capture and submit an enrollment request using the stale `user_data`/`operator_data`, because the freshness check only compares wall-clock elapsed time against a large static threshold — it never re-queries `backend::user_status` to confirm the decision is still valid. This can result in an enrollment being attributed/authorized under stale session data (misattributed or unauthorized signup submission), and biometric capture happening under an authorization context that the backend would no longer consider valid at PCP-key/session level (the `backend_keys`/`self_custody_public_key` used to encrypt the PCP are also locked in at the original validation time).

### Likelihood Explanation
This requires no privileged access — it is reachable by the normal operator/user QR-scanning flow that every signup goes through, and the reuse window (23 hours by default) is generous. The likelihood of the window being exploited by an active attacker depends on how quickly backend-side session state can become stale/invalidated versus this local timer, which is not otherwise cross-checked; this is uncertain without visibility into the backend's session semantics (which is outside this repo). The severity is also somewhat mitigated by the backend performing its own checks at `signup_post`/`signup_poll` time, but the request itself (`src/backend/signup_post.rs:98-161`) does not re-run the `user_status` validity/authorization check — it only reports `SoftwareVersionStatus`; whether the backend independently re-validates session/user status for revocation at that point cannot be confirmed from this repo alone.

### Recommendation
Re-validate the cached `user_data`/`operator_data` against the backend (`backend::user_status::request`) immediately before committing to the enrollment (i.e., right before `enroll_user::Plan::run`/`signup_post::request`), rather than relying solely on a fixed elapsed-time cutoff (`operator_qr_expiration_time`). At minimum, shorten the reuse window and treat it as a UX optimization only, not as an authorization decision; the authoritative check should be performed at execution time, analogous to recomputing claimable share at claim time in the referenced report.

### Proof of Concept
Not independently reproducible from static analysis alone — the exploitability hinges on backend-side session semantics (i.e., whether a `user_status`/session validity decision can become stale within the `operator_qr_expiration_time` window) which is not observable in this repository. Conceptually:
1. Operator+user scan QR codes; `backend::user_status::request` returns `valid: true` with `user_data`, cached in `QrCodes::Both` with `timestamp = Instant::now()`.
2. The user's backend session/authorization state changes (e.g., revoked) shortly after.
3. Because `operator_data.timestamp.elapsed() < operator_qr_expiration_time` (up to 23 hours), `scan_remaining_qr_codes` (`src/plans/mod.rs:796-805`) returns the stale `user_data` without re-querying the backend.
4. `do_signup` proceeds through biometric capture and calls `signup_post::request` using this stale, no-longer-authorized session context.

Given the uncertainty about whether the backend independently re-validates at `signup_post`/`signup_poll` time, this should be treated as a **caching/staleness weakness requiring backend confirmation** rather than a fully proven exploit.

### Citations

**File:** src/plans/mod.rs (L794-805)
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
```

**File:** src/plans/mod.rs (L1580-1622)
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
            }
            Ok(None) => {
                orb.ui.qr_scan_fail(QrScanSchema::User);
                dd_incr!("main.count.signup.result.failure.user_qr_code", "type:invalid_qr");
            }
            Err(_) => {
                orb.ui.qr_scan_fail(QrScanSchema::User);
                dd_incr!(
                    "main.count.signup.result.failure.user_qr_code",
                    "type:validation_network_error"
                );
            }
        }
        Ok(None)
```
