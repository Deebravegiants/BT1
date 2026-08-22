### Title
Stale cached operator-QR authorization is reused across multiple signups without re-validation until an expiration timer elapses - (File: src/plans/mod.rs)

### Summary
The external report describes a "late sync" bug class: a periodic state-boundary function (`syncRewards()`) is only re-evaluated on a timer/expiry check rather than on every state-changing action, so stale state computed for one "cycle" gets unfairly applied to actors that should belong to the next cycle (or vice-versa). The orb-core analog is the operator-QR authorization cache: the operator's identity/location validity is fetched once from the backend and then reused for every subsequent signup as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, without re-querying the backend per signup.

### Finding Description
`MasterPlan::run` scans the operator QR code once and stores the result (`OperatorData { qr_code, location_data, timestamp }`), then loops through many idle/signup cycles reusing that same cached `operator_data` as long as it has not expired: [1](#0-0) 

The expiration check is a simple elapsed-time comparison against `operator_qr_expiration_time` (a backend-configurable value, defaulting to 23 hours): [2](#0-1) [3](#0-2) 

The same stale-cache pattern is repeated in `scan_remaining_qr_codes`, which explicitly reuses `operator_data` for `QrCodes::Both`/`QrCodes::Operator` variants purely based on `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, bypassing a fresh call to the backend operator-status endpoint (`backend::operator_status::request`, which is what actually determines `valid`/`location_data`) for every new signup: [4](#0-3) [5](#0-4) 

This mirrors the `TokenggAVAX.syncRewards()` root cause exactly: a boundary-state value (`lastSync`/`rewardsCycleEnd` there; `operator_data`/`timestamp` here) is only "re-synced" against ground truth (`syncRewards()` call there; `operator_status::request` here) on a coarse timer, and every action taken before that re-sync (deposits/withdrawals there; signups here) is attributed to the stale state instead of being individually re-validated.

### Impact Explanation
If an operator's authorization is revoked or their location/validity status changes on the backend (e.g., the operator is suspended for fraud, loses permission, or their location no longer matches the required region) mid-shift, the orb continues to accept and process new, unrelated signups under the previously cached, now-stale operator authorization for up to `operator_qr_expiration_time` (23 hours by default) instead of re-checking authorization for each new signup. This allows signups to be misattributed to/authorized by an operator identity that is no longer valid, i.e., a cross-signup "state bleed" of stale authorization data into signup sessions that should have been blocked or attributed differently. This is directly analogous to the "early vs late" unfair-attribution class in the source report, translated to signup authorization rather than reward shares.

### Likelihood Explanation
The behavior is triggered by ordinary, expected orb operation (multiple signups performed back-to-back in normal or self-serve mode) — no attacker action or malicious node/hardware access is required, and it is fully within the unprivileged-user-facing signup flow. The only precondition is that the operator's backend-side authorization state changes between the initial QR scan and expiration of the locally cached timer, which is a realistic operational scenario (revocation, location change, policy update) rather than a contrived edge case.

### Recommendation
Re-validate operator authorization (via `backend::operator_status::request`) at the start of each individual signup (or at minimum on a much shorter interval) instead of relying solely on the long-lived `operator_qr_expiration_time` cache. This closes the gap where a stale authorization state can back new signups after the operator's true status has changed on the backend.

### Proof of Concept
1. Operator scans QR code; `scan_initial_qr_codes` fetches valid `OperatorData` and caches it with `timestamp = Instant::now()` [6](#0-5) .
2. Backend revokes/changes the operator's authorization shortly after (e.g., operator flagged for fraud).
3. `MasterPlan::run` loops back into `idle_wait_for_signup_request` → `scan_remaining_qr_codes`, which sees `operator_data.timestamp.elapsed() < operator_qr_expiration_time` still true, and reuses the now-invalid cached `operator_data` without calling `operator_status::request` again [7](#0-6) .
4. A new signup proceeds and is authorized/attributed under the stale operator identity for up to 23 hours (default `operator_qr_expiration_time`), until the cache finally expires and forces a re-scan.

### Citations

**File:** src/plans/mod.rs (L343-364)
```rust
        orb.enable_data_uploader()?;
        let mut initial_qr_codes = QrCodes::None;
        loop {
            self.scan_initial_qr_codes(
                orb,
                &mut initial_qr_codes,
                self_serve,
                operator_qr_expiration_time,
            )
            .await?;
            let Some(qr_codes) = self
                .idle_wait_for_signup_request(
                    orb,
                    &initial_qr_codes,
                    self_serve,
                    self_serve_button,
                    operator_qr_expiration_time,
                )
                .await?
            else {
                continue;
            };
```

**File:** src/plans/mod.rs (L749-786)
```rust
    async fn scan_initial_qr_codes(
        &mut self,
        orb: &mut Orb,
        qr_codes: &mut QrCodes,
        self_serve: bool,
        operator_qr_expiration_time: Duration,
    ) -> Result<()> {
        if self_serve
            && qr_codes
                .operator_timestamp()
                .map_or(true, |ts| ts.elapsed() > operator_qr_expiration_time)
        {
            loop {
                let qr_capture_start = Instant::now();
                let operator_qr_code =
                    self.scan_operator_qr_code(orb, None).await?.expect("to never timeout");
                let Some(operator_qr_code) =
                    self.handle_magic_operator_qr_code(orb, operator_qr_code).await?
                else {
                    continue;
                };
                let Some((_, operator_location_data)) =
                    self.verify_operator_qr_code(orb, &operator_qr_code, qr_capture_start).await?
                else {
                    continue;
                };
                *qr_codes = QrCodes::Operator {
                    operator_data: OperatorData {
                        qr_code: operator_qr_code,
                        location_data: operator_location_data,
                        timestamp: Instant::now(),
                    },
                };
                break;
            }
        }
        Ok(())
    }
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

**File:** src/config.rs (L440-444)
```rust
            orb_relay_shutdown_wait_for_shutdown: Duration::from_millis(1500),
            orb_relay_announce_orb_id_retries: 3,
            orb_relay_announce_orb_id_timeout: Duration::from_millis(2000),
            operator_qr_expiration_time: Duration::from_secs(60 * 60 * 23),
        }
```

**File:** src/backend/operator_status.rs (L33-66)
```rust
/// Operator ID validation status.
#[derive(Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Status {
    /// Whether the operator ID is valid.
    pub valid: bool,
    /// Location data of the operator.
    pub location_data: Option<LocationData>,
    /// If 'valid == false', the 'reason' field contains the reason for the invalidation.
    pub reason: Option<String>,
}

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
```
