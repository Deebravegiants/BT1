### Title
Unauthenticated `signup_extension` flag in QR-code parsing bypasses operator/user backend authorization and fraud/liveness checks - (File: `src/plans/qr_scan/user.rs`, `src/plans/mod.rs`)

### Summary
The reported zkSync bug is a missing constraint: the `shr` circuit derives a quotient/remainder pair via an unconstrained witness value and never enforces `remainder < divisor`, so a malicious prover can set the result to any value ≤ the correct one, bypassing the circuit's supposed guarantee. The analogous class of bug — a value that is supposed to be constrained/validated but is accepted unchecked and then used to bypass a security-critical gate — exists in orb-core's QR-code "signup extension" handling. The `signup_extension` flag and `SignupExtensionConfig`, derived purely from unauthenticated, attacker-controlled QR-code text (no cryptographic signature, no backend round-trip), are used as an unconstrained boolean that flips code paths to skip backend operator/user authorization checks and to skip the entire biometric fraud/liveness pipeline while still marking the signup as successful.

### Finding Description
When the `internal-data-acquisition` feature is compiled in, `Data::try_parse` in `src/plans/qr_scan/user.rs` matches an additional regex `QR_CODE_SIGNUP_EXTENSION` that accepts an essentially attacker-chosen `user_id` string and an unauthenticated `mode`/`parameters` suffix, producing `signup_extension: true` and a `SignupExtensionConfig` purely from local string parsing: [1](#0-0) [2](#0-1) [3](#0-2) 

No cryptographic binding, signature, or backend confirmation is required for this flag — unlike the normal QR path which goes through `decode_qr` or a backend `user_status`/`operator_status` request.

This unconstrained flag is then used to short-circuit the two critical authorization gates:

1. Operator identity verification is skipped entirely whenever the presented operator QR-code itself carries `signup_extension() == true`: [4](#0-3) 

2. User QR-code backend validation (`backend::user_status::request`) is likewise skipped whenever both operator and user QR carry the flag, returning a locally fabricated `UserData::default()` instead of anything backend-attested: [5](#0-4) 

3. Most critically, in `do_signup`, once `debug_report.signup_extension_config` is set (derived from the same unauthenticated flag), the entire biometric pipeline — including fraud detection and liveness checks — is skipped, and the signup is marked successful based only on having captured *something*: [6](#0-5) 

The parallel to the reported bug is structural: in both cases, a value that should be bound by an explicit validation constraint (`remainder < divisor` in the circuit; "is this QR code cryptographically/backend authorized" in orb-core) is instead accepted directly from attacker-supplied input and used unchecked to control a security-relevant branch, letting the "prover"/QR-presenter pick any outcome up to and including full bypass.

### Impact Explanation
An unprivileged individual who can present two QR codes to the orb's camera (one formatted to satisfy `QR_CODE_SIGNUP_EXTENSION` as the "operator" scan and one as the "user" scan) can:
- Forge operator legitimacy without any backend check (`verify_operator_qr_code` returns `Ok(Some(...))` unconditionally when `signup_extension()` is true),
- Forge user identity/authorization without any backend check (`handle_user_qr_code` fabricates `UserData::default()`),
- Cause the signup to be recorded as successful (`result.success = true`) while skipping fraud detection and the full biometric pipeline (`detect_fraud`, `biometric_pipeline`).

This is a concrete cross-cutting bypass of signup authorization and fraud/liveness enforcement driven entirely by unauthenticated QR-code content, matching the accepted impact categories (unauthorized/misattributed signup, fraud/liveness bypass).

### Likelihood Explanation
This path only exists when the orb is built with the `internal-data-acquisition` Cargo feature, which is a genuine (non-test) production feature referenced across core files (`src/agents/image_notary.rs`, `src/brokers/orb.rs`, `src/bin/orb-core.rs`, `src/plans/idle.rs`), not gated behind `#[cfg(test)]`. Any fleet or orb build that enables this feature (e.g., research/data-acquisition orbs) is exposed. Exploitation requires only the ability to present crafted QR-code text to the camera during a signup attempt — no privileged access, hardware tampering, or operator credentials are needed, satisfying the "unprivileged user" scope.

### Recommendation
- Require that `signup_extension` / `SignupExtensionConfig` derived from QR-code text be additionally corroborated by a backend call (as is done for normal operator/user QR codes) before being allowed to bypass `verify_operator_qr_code` or `verify_user_qr_code`.
- Do not allow `signup_extension_config.is_some()` alone to skip `detect_fraud`/`biometric_pipeline` in `do_signup`; gate this behind a backend-confirmed, signed authorization rather than a locally-parsed string flag.
- If the intent is to support internal-only data-acquisition orbs, ensure the feature is strictly excluded from any production/customer-facing build and cannot be toggled at runtime based on scanned QR content alone.

### Proof of Concept
1. Build orb-core with `--features internal-data-acquisition`.
2. During the "scan operator QR" step, present a QR code such as `userid:attacker-op:1::0::` — this matches `QR_CODE_SIGNUP_EXTENSION` in `src/plans/qr_scan/user.rs`, producing `Data { user_id: "attacker-op", signup_extension: true, signup_extension_config: Some(..) }`.
3. `verify_operator_qr_code` (`src/plans/mod.rs:1551-1557`) short-circuits, returning `Ok(Some(...))` with a fabricated `LocationData` — no backend call is made to `backend::operator_status::request`.
4. During the "scan user QR" step, present a similarly crafted QR code, e.g. `userid:attacker-user:1::0::`.
5. `handle_user_qr_code` (`src/plans/mod.rs:1060-1073`) detects both operator and user QR have `signup_extension() == true`, and returns `backend::user_status::UserData::default()` without calling `backend::user_status::request`.
6. `do_signup` proceeds to `biometric_capture`, then at line 558 sees `debug_report.signup_extension_config.is_some()` is true and immediately sets `result.success = true`, skipping `detect_fraud` and `biometric_pipeline` entirely. [6](#0-5)

### Citations

**File:** src/plans/qr_scan/user.rs (L38-60)
```rust
#[cfg(any(feature = "internal-data-acquisition", test))]
static QR_CODE_SIGNUP_EXTENSION: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"(?x)
            ^
            userid
            :
            (?P<user_id>
                [a-z0-9_-]+
            )
            :
            (?P<data_policy>\d{1,10})
            (::
                (?P<mode>[a-z0-9]+)
                (:
                    (?P<parameters>[a-z0-9:]+)
                )?
            )?
            ::$
        ",
    )
    .expect("bad regex")
});
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

**File:** src/plans/qr_scan/user.rs (L144-157)
```rust
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

**File:** src/plans/mod.rs (L553-561)
```rust
        let capture = self.biometric_capture(orb, debug_report).await?;
        self.after_biometric_capture(orb, debug_report, capture.is_some(), self_serve).await?;
        let Some(capture) = capture else {
            return Ok(result);
        };
        if self.skip_pipeline() || debug_report.signup_extension_config.is_some() {
            result.success = true;
            return Ok(result);
        }
```

**File:** src/plans/mod.rs (L1060-1073)
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
