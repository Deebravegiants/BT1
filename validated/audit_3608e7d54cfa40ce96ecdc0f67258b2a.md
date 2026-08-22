### Title
Missing upper bound on backend-configurable `operator_qr_expiration_time` allows indefinitely-reusable operator authorization - (File: src/config.rs)

### Summary
The Orb downloads `operator_qr_expiration_time` from the management backend and uses it to decide how long a previously scanned operator QR-code's authorization (`OperatorData`) remains valid for starting new signups without re-scanning/re-verifying the operator. `Config::validate` only checks the `sound_volume` field and imposes no upper bound on `operator_qr_expiration_time` (or any other timing field), so a misconfigured or erroneous backend value can make the operator authorization effectively never expire, mirroring the reported `setPaymentWindow` bug class where an unbounded, remotely-settable time window removes a critical time-based safety guarantee.

### Finding Description
`operator_qr_expiration_time` is defined as a `Duration` field on `Config` [1](#0-0) , populated straight from the backend response with only a default fallback and no clamping to any maximum [2](#0-1) . The only validation performed on the whole `Config` struct is a bound check on `sound_volume`; no bound is enforced on `operator_qr_expiration_time` or any other duration field [3](#0-2) .

This value directly governs the trust window during which a previously captured operator QR-code / location data (`OperatorData`) is treated as still authorized to gate new signups. In `scan_initial_qr_codes`, the orb only re-scans the operator QR when the elapsed time since the last scan exceeds `operator_qr_expiration_time` [4](#0-3) . Likewise, `scan_remaining_qr_codes` reuses the same cached `OperatorData` for a full signup as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time` [5](#0-4) , and the idle self-serve user-QR loop computes its own remaining timeout from the same value [6](#0-5) .

The default value is already 23 hours [7](#0-6) , and because no upper bound is enforced anywhere in `from_backend` or `validate`, the backend can set an arbitrarily larger (or effectively unlimited) value, which the Orb will accept and use verbatim.

### Impact Explanation
If `operator_qr_expiration_time` is pushed to an excessively large value (deliberately or by misconfiguration), an operator's one-time QR scan authorization persists far longer than intended. In self-serve mode this lets the signup flow keep treating the location/operator authorization as fresh for the extended period, allowing repeated or later signups to proceed under stale operator-authorization state without a fresh scan/re-verification of the operator. This weakens the freshness guarantee that ties a signup to a currently-present, currently-verified operator, which is the analog of the reported issue: an unbounded, remotely-settable time window undermines a security-relevant expiry that the rest of the system depends on for correctness/trust.

### Likelihood Explanation
This requires the management backend to push an excessively large `operator_qr_expiration_time` (a config value that is deserialized and used without any range validation), a plausible occurrence given a simple operational error or unvetted override, exactly as in the original report's `setPaymentWindow` scenario where the contract owner accidentally set the window too high.

### Recommendation
Enforce an explicit maximum bound on `operator_qr_expiration_time` (and ideally all backend-supplied timeout/expiration `Duration` fields) inside `Config::validate` or when mapping the field in `Config::from_backend`, clamping or rejecting values above a sane ceiling instead of accepting whatever the backend sends unchecked.

### Proof of Concept
1. Backend config endpoint response sets `OperatorQrExpirationTime` to a very large millisecond value (e.g. `u64::MAX` or several years).
2. `Config::from_backend` maps it directly via `Duration::from_millis` with no clamp [2](#0-1) .
3. `Config::validate` passes because it only checks `sound_volume` [3](#0-2) .
4. `scan_initial_qr_codes`/`scan_remaining_qr_codes` now treat any previously scanned operator QR as valid for that near-infinite duration, reusing stale `OperatorData` across many signups without requiring a fresh operator scan [5](#0-4) .

### Citations

**File:** src/config.rs (L134-135)
```rust
    /// Expiration time for the operator QR code.
    pub operator_qr_expiration_time: Duration,
```

**File:** src/config.rs (L283-284)
```rust
            operator_qr_expiration_time: operator_qr_expiration_time
                .map_or(default.operator_qr_expiration_time, Duration::from_millis),
```

**File:** src/config.rs (L322-326)
```rust
    /// Validates the configuration.
    #[must_use]
    pub fn validate(&self) -> bool {
        self.basic_config.sound_volume <= MAX_SOUND_VOLUME
    }
```

**File:** src/config.rs (L443-443)
```rust
            operator_qr_expiration_time: Duration::from_secs(60 * 60 * 23),
```

**File:** src/plans/mod.rs (L456-468)
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
```

**File:** src/plans/mod.rs (L749-760)
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
```

**File:** src/plans/mod.rs (L796-808)
```rust
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
```
