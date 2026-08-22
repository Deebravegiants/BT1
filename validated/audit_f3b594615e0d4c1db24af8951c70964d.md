### Title
Unbounded `operator_qr_expiration_time` from backend config allows indefinite reuse of stale operator authorization/location data across signups - (File: src/config.rs)

### Summary
`operator_qr_expiration_time` is a `Duration` field entirely controlled by the management backend response and consumed by `Config::from_backend` with no minimum or maximum clamp, unlike other numeric fields in the same function (e.g. `sound_volume`, `fan_max_speed`) which are explicitly clamped. [1](#0-0) [2](#0-1)  This value governs how long a single validated operator QR-code and its associated `location_data` (`OperatorData`) remain valid for reuse across multiple, distinct user signups without re-verification.

### Finding Description
`operator_qr_expiration_time` is declared in the `Config` struct and defaults to 23 hours, but the backend-supplied override is applied without any bound. [3](#0-2) [4](#0-3)  The backend response type carries it as a raw optional `u64` millisecond value with no validation on the wire either. [5](#0-4) 

This parameter directly controls the reuse window of `operator_data` (which contains the operator's `qr_code` and `location_data`, captured once at `Instant::now()`), both when scanning initial QR codes and remaining QR codes for subsequent signups: [6](#0-5) [7](#0-6) 

The reused `operator_data.location_data` is then passed, unverified again, into the user QR-code validation request whenever `user_qr_validation_use_only_operator_location` is enabled (which is the default): [8](#0-7) [9](#0-8) [10](#0-9) 

Because there is no `MIN`/`MAX` enforced on `operator_qr_expiration_time` (analogous to the missing `MIN_FORK_PERIOD` in the Nouns DAO report), a value set arbitrarily high by the backend causes the orb to keep treating a single, possibly stale, operator authorization event and its captured session coordinates as valid indefinitely, re-using them to gate and geolocate every subsequent user signup without any re-verification of the operator's continued physical presence or authorization.

### Impact Explanation
If `operator_qr_expiration_time` is pushed to an unreasonably large value, the orb will validate an unbounded number of subsequent, independent user signups against a single, one-time operator QR verification and a single, stale set of session coordinates, instead of requiring periodic re-verification. This creates a cross-signup state bleed: many logically distinct signup sessions are validated using authorization/location state captured once, arbitrarily long ago, which can misattribute signups to a location/operator context that no longer reflects reality (e.g., orb relocated, or operator credential no longer legitimate) — undermining the location-based fraud check performed via `user_qr_validation_use_only_operator_location`.

### Likelihood Explanation
This requires the value to be set by the management backend (a privileged, trusted source in the orb's threat model), so exploitation requires either a compromised/misconfigured backend or an unintentional misconfiguration — comparable to the low-likelihood-but-high-impact rating given to the original Nouns DAO finding, since the code path itself performs no independent sanity check on the received duration.

### Recommendation
Enforce a sane minimum and maximum bound on `operator_qr_expiration_time` when parsing the backend config in `Config::from_backend`, mirroring the existing clamps used for `sound_volume` and `fan_max_speed`. [2](#0-1)  Additionally, consider re-verifying operator location/authorization at fixed intervals regardless of the configured expiration, rather than relying solely on the backend-controlled duration.

### Proof of Concept
1. Backend config endpoint response sets `operatorQrExpirationTime` to an extremely large millisecond value (e.g. `u64::MAX` or several years). [5](#0-4) 
2. `Config::from_backend` maps this directly to a `Duration` with no clamping. [1](#0-0) 
3. The orb performs one legitimate operator QR scan/verification, populating `OperatorData` with `location_data` and a timestamp. [11](#0-10) 
4. For every following signup, since `operator_data.timestamp.elapsed() < operator_qr_expiration_time` is always true, the orb skips operator re-verification and reuses the original `operator_data` (including its `location_data`) for all subsequent, unrelated user signups. [7](#0-6)

### Citations

**File:** src/config.rs (L134-135)
```rust
    /// Expiration time for the operator QR code.
    pub operator_qr_expiration_time: Duration,
```

**File:** src/config.rs (L206-213)
```rust
                sound_volume: sound_volume.clamp(0, MAX_SOUND_VOLUME),
                language,
            },
            operation_country: operation_country.or(default.operation_country),
            operation_city: operation_city.or(default.operation_city),
            fan_max_speed: Some(
                fan_max_speed.unwrap_or(DEFAULT_MAX_FAN_SPEED).clamp(0.0, DEFAULT_MAX_FAN_SPEED),
            ),
```

**File:** src/config.rs (L283-284)
```rust
            operator_qr_expiration_time: operator_qr_expiration_time
                .map_or(default.operator_qr_expiration_time, Duration::from_millis),
```

**File:** src/config.rs (L437-438)
```rust
            user_qr_validation_use_full_operator_qr: false,
            user_qr_validation_use_only_operator_location: true,
```

**File:** src/config.rs (L443-443)
```rust
            operator_qr_expiration_time: Duration::from_secs(60 * 60 * 23),
```

**File:** src/backend/config.rs (L74-75)
```rust
    pub operator_qr_expiration_time: Option<u64>,
    pub last_updated: u64,
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

**File:** src/plans/mod.rs (L794-820)
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

**File:** src/plans/mod.rs (L849-853)
```rust
                    let operator_data = OperatorData {
                        qr_code: operator_qr_code,
                        location_data: operator_location_data,
                        timestamp: Instant::now(),
                    };
```

**File:** src/plans/mod.rs (L1587-1598)
```rust
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
```

**File:** src/backend/user_status.rs (L119-125)
```rust
    let request = if use_only_operator_location {
        super::client()?
            .get(format!("{}/api/v2/session/{}/status", *SIGNUP_BACKEND_URL, qr_code.user_id,))
            .query(&[
                ("lat", operator_data.location_data.session_coordinates.latitude),
                ("lon", operator_data.location_data.session_coordinates.longitude),
            ])
```
