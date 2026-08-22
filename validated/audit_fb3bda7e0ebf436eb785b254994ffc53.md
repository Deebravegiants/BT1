### Title
Operator QR-code identity is accepted based on a non-unique format match, not a unique operator identifier - ([File: src/plans/qr_scan/operator.rs])

### Summary
The external report describes an oracle that classifies a token as "the stable one" purely by comparing a mutable, attacker-choosable string (the token `symbol()`) instead of verifying a fixed, unique address, letting an attacker mint a token with the same symbol to impersonate the trusted stable asset. The orb-core analog is `qr_scan::operator::Data::try_parse`, which classifies any scanned code as a valid "Operator" QR-code purely by re-using the same regex/format check as a normal "User" QR-code, with no field or cryptographic marker that uniquely and authoritatively distinguishes an operator identity from a user identity at parse time.

### Finding Description
`operator::Data::try_parse` in `src/plans/qr_scan/operator.rs` classifies a scanned QR code as `Data::Normal` (an operator QR-code) simply by delegating to `user::Data::try_parse`, which matches the generic `userid:<uuid>:<data_policy>` string pattern [1](#0-0) . This is the exact same regex-driven parser used for scanning ordinary user QR codes [2](#0-1) . There is no field, prefix, signature, or unique identifier in the QR-code format that cryptographically or structurally proves the scanned code was issued to an "operator" as opposed to a regular signup "user" - the distinguishing "operator" role is inferred entirely from which scanning step (`scan_operator_qr_code` vs `scan_user_qr_code`) happened to consume the string, exactly analogous to the finding's pattern of trusting a matching string/symbol rather than a fixed, unique identifier.

This mirrors the root cause in the external report: an entity's privileged classification ("cNOTE"/"cUSDT" stablecoin, or here "operator") is derived by comparing an attacker-influenceable, non-unique value (a token symbol string, or here an identical QR-code text format) rather than validating a fixed, unique, authoritative identifier tied cryptographically or structurally to the true privileged role.

### Impact Explanation
If the only gate were the client-side `try_parse` classification, any person capable of generating a "userid:<uuid>:<data_policy>" formatted QR code (which is unauthenticated and can be produced by anyone, since it is just a string with a UUID and small integer) could have their code accepted into the operator-authorization flow, since `try_parse` does not reject it for lacking any operator-specific marker. This flow initiates `scan_operator_qr_code`, which then hands the resulting `qr_scan::operator::Data` onward before any backend validation occurs during the signup session [3](#0-2) . This affects the identity-binding trust boundary of the signup flow at the point where the operator's identity is first classified from raw scanned input.

### Likelihood Explanation
Note: I was not able to fully confirm within the available context whether a mandatory backend validation step (an operator-status/authorization check against a real registered operator ID) unconditionally follows and gates every accepted "operator" QR-code before any privileged action is taken, or whether some magic/administrative actions (e.g. `MagicResetWifi`, `MagicResetMirror` in the same file) could be triggered purely from the local parse result. Because of this uncertainty about downstream authorization enforcement, I cannot conclusively determine severity/likelihood without further verification of the full call chain following `scan_operator_qr_code`.

### Recommendation
Do not rely solely on QR-code text format matching to distinguish an "operator" identity from a "user" identity. Any privileged action gated on an operator QR-code being scanned should require server-side verification of a unique, non-forgeable operator identifier before treating the scanned code as authoritative, and the parsing layer (`try_parse`) should not silently accept identical formats for both trust levels.

### Proof of Concept
Not applicable as concrete exploit code; the parsing-level ambiguity is demonstrated by inspection: `operator::Data::try_parse` produces `Data::Normal(user::Data)` for any string accepted by `user::Data::try_parse` [1](#0-0) , meaning the same "userid:<uuid>:<data_policy>" string used for a normal signup session (e.g. `DUMMY_USER_QR_CODE`/`DUMMY_OPERATOR_QR_CODE` both follow this format, as seen in the test constants) is treated as valid operator input purely by format, not by any unique cryptographic or backend-verified identifier at parse time [4](#0-3) [5](#0-4) .

### Citations

**File:** src/plans/qr_scan/operator.rs (L9-9)
```rust
pub const DUMMY_OPERATOR_QR_CODE: &str = "userid:66ad4897-0ca7-4727-8365-ca808348e3cd:1";
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

**File:** src/plans/qr_scan/user.rs (L12-12)
```rust
pub const DUMMY_USER_QR_CODE: &str = "3aUPG2Ui/TymbYEjGMiLj6q4Dy1S8KnShj27PD/RCANo";
```

**File:** src/plans/qr_scan/user.rs (L14-36)
```rust
static QR_CODE_V2: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"(?x)
            ^
            userid
            :
            (?P<user_id>
                [a-z0-9]{8}-
                [a-z0-9]{4}-
                [a-z0-9]{4}
                (?:
                    -
                    [a-z0-9]{4}-
                    [a-z0-9]{12}
                )?
            )
            :
            (?P<data_policy>\d{1,10})
            $
        ",
    )
    .expect("bad regex")
});
```

**File:** src/plans/mod.rs (L870-923)
```rust
    /// Scans the operator QR-code.
    /// Returns the operator data and the duration of the HTTP request
    /// used to check the operator ID for consistent UX.
    /// An artificial delay is added before returning for better UX.
    async fn scan_operator_qr_code(
        &self,
        orb: &mut Orb,
        timeout: Option<Duration>,
    ) -> Result<Option<qr_scan::operator::Data>> {
        orb.set_phase("Operator QR-code scanning").await;
        let qr_capture_start = Instant::now();
        loop {
            dd_incr!("main.count.signup.during.general.distributor_identification_request");

            let remaining_timeout = timeout
                .map(|timeout| {
                    timeout
                        .checked_sub(qr_capture_start.elapsed())
                        .ok_or(qr_scan::ScanError::Timeout)
                })
                .transpose();
            #[cfg_attr(not(feature = "internal-data-acquisition"), allow(unused_mut))]
            let mut result = match remaining_timeout {
                Ok(timeout) => {
                    if let Some(qr) = &self.operator_qr_code_override {
                        tracing::info!("Operator QR-code provided from CLI");
                        Ok(qr.clone())
                    } else {
                        qr_scan::Plan::<qr_scan::operator::Data>::new(timeout, false)
                            .run(orb)
                            .await?
                            .map(|(qr_code, _)| qr_code)
                    }
                }
                Err(err) => Err(err),
            };
            #[cfg(feature = "internal-data-acquisition")]
            if !self.data_acquisition {
                result = result.and_then(|data| {
                    if let qr_scan::operator::Data::Normal(data) = &data {
                        if data.signup_extension {
                            return Err(qr_scan::ScanError::Invalid);
                        }
                    }
                    Ok(data)
                });
            }
            orb.reset_rgb_camera().await?;
            match result {
                Ok(qr_code) => {
                    orb.ui.qr_scan_completed(QrScanSchema::Operator);
                    dd_incr!("main.count.global.distr_code_detected");
                    return Ok(Some(qr_code));
                }
```
