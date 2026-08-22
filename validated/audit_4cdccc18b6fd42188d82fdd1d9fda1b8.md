## Title
Signup-extension QR-code bypasses backend user-identity verification, allowing unauthenticated/unauthorized signup binding - (File: src/plans/mod.rs)

### Summary
The `ReserveFeed.setExchangeRate` report describes a state-mutating function reachable by any unprivileged caller with no authorization/verification check. The closest reachable analog in orb-core is `MasterPlan::handle_user_qr_code`, which accepts a "signup-extension" user/operator QR-code pair and — instead of routing through the backend identity-verification call (`verify_user_qr_code` → `backend::user_status::request`) — directly returns a default, unauthenticated `UserData` for the signup to proceed with.

### Finding Description
Normal signup flow requires the scanned user QR-code to be validated against the backend, which checks a HMAC/signature-style `user_data_hash` binding (`user_data.verify(user_data_hash)`) before any identity data (public keys, `identity_commitment`, etc.) is trusted: [1](#0-0) 

However, when both the operator QR-code and the user QR-code declare a "signup extension" mode (a locally-parsed regex format, not a backend-signed token), `handle_user_qr_code` short-circuits this verification entirely and fabricates a default `UserData` for the signup: [2](#0-1) 

The signup-extension QR format is parsed purely locally via regex (`QR_CODE_SIGNUP_EXTENSION`), with no signature or backend round-trip: [3](#0-2) [4](#0-3) 

This mirrors the root cause of the reported bug class: a state-affecting operation (here, establishing the trusted identity/user-data binding for a signup) that skips the access-control/verification step (`verify_user_qr_code`/backend `valid` + `user_data.verify` check) that every other code path enforces.

### Impact Explanation
If reachable, this allows an operator/user pair to force a signup to proceed with attacker-controlled `user_id` and no backend-issued identity binding (`identity_commitment`, `self_custody_public_key`, encrypted key material are all `None`/default), i.e., cross-signup identity binding could be forged or bypassed, similar in spirit to the disclosed `setExchangeRate` issue where an unauthorized party controls state that should be gated. This would let an unprivileged QR presenter dictate the "authenticated" user identity for the resulting biometric package without backend consent.

### Likelihood Explanation
This path is fully gated behind the `internal-data-acquisition` Cargo feature (`#[cfg(feature = "internal-data-acquisition")]`) both for regex parsing of `QR_CODE_SIGNUP_EXTENSION` and for the `signup_extension` field defaulting to `true`. I could not verify from the indexed code whether this feature is compiled into production Orb builds or is strictly a research/internal-only build flag — this is a significant uncertainty. If it is compiled into production firmware and reachable via a physically presented QR code, likelihood is moderate (requires physical access/QR presentation, not remote network access). If it is dev/test-only, per the scan rules ("test-only paths" are out of scope) this would not qualify as a valid analog.

### Recommendation
If `internal-data-acquisition` is ever enabled in production builds, require the signup-extension path to still go through backend verification (or an equivalent signed-token check) rather than returning a default, unverified `UserData`. At minimum, ensure this feature flag cannot be enabled in production Orb firmware builds, and add an explicit, code-level assertion/compile-time guard preventing this bypass from ever using un-authenticated identity data.

### Proof of Concept
Not independently verifiable from the indexed code alone — reproducing requires confirming the `internal-data-acquisition` feature is enabled in a shipped build, then presenting an operator QR-code and a user QR-code both matching the `QR_CODE_SIGNUP_EXTENSION` regex (e.g. `userid:<uuid>:<policy>::<mode-hex>::`), at which point `handle_user_qr_code` returns `Some(Some((user_qr_code, UserData::default(), ...)))` without calling `backend::user_status::request`.

**Caveat on confidence:** I could not confirm from the available index whether `internal-data-acquisition` is enabled in any production configuration, whether additional upstream gating exists (e.g., only reachable in lab/test units), or whether downstream code paths (e.g., `enroll_user`, `personal_custody_package`) still reject a signup lacking backend-issued keys before any biometric data is persisted/uploaded. Given the "reject test-only paths" rule and the strong feature-gating observed, this finding should be treated as **low-to-moderate confidence** rather than a confirmed production vulnerability. If a Devin session can confirm the feature is prod-disabled and that downstream code paths (e.g. `TryInto<personal_custody_package::Credentials>` at `src/plans/mod.rs:1898-1938`, which requires all backend keys to be `Some`) reject the resulting default `UserData` before any package is built, this finding should likely be downgraded to no-impact, per the exclusion rules. [5](#0-4)

### Citations

**File:** src/backend/user_status.rs (L163-179)
```rust
    if let (Some(backend_keys), Some(user_data)) = (backend_keys, authenticated_app_data) {
        tracing::info!("User QR-data: {user_data:?}");

        #[cfg(not(feature = "skip-user-qr-validation"))]
        {
            let Some(user_data_hash) = &qr_code.user_data_hash else {
                tracing::error!(
                    "image_self_custody is provided by backend, but got no user_data_hash from \
                     QR-code"
                );
                return Ok(None);
            };
            if !user_data.verify(user_data_hash) {
                tracing::error!("user_data verification failure");
                return Ok(None);
            }
        }
```

**File:** src/plans/mod.rs (L1060-1083)
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
```

**File:** src/plans/mod.rs (L1898-1938)
```rust
impl TryInto<personal_custody_package::Credentials> for ResolvedQrCodes {
    type Error = ();

    fn try_into(self) -> Result<personal_custody_package::Credentials, Self::Error> {
        let ResolvedQrCodes { operator_data, user_data, user_qr_code, user_qr_code_string } = self;
        if let (
            Some(backend_iris_public_key),
            Some(backend_iris_encrypted_private_key),
            Some(backend_normalized_iris_public_key),
            Some(backend_normalized_iris_encrypted_private_key),
            Some(backend_face_public_key),
            Some(backend_face_encrypted_private_key),
            Some(self_custody_user_public_key),
        ) = (
            user_data.backend_iris_public_key,
            user_data.backend_iris_encrypted_private_key,
            user_data.backend_normalized_iris_public_key,
            user_data.backend_normalized_iris_encrypted_private_key,
            user_data.backend_face_public_key,
            user_data.backend_face_encrypted_private_key,
            user_data.self_custody_user_public_key,
        ) {
            Ok(personal_custody_package::Credentials {
                operator_qr_code: operator_data.qr_code,
                user_qr_code,
                user_qr_code_string,
                backend_iris_public_key,
                backend_iris_encrypted_private_key,
                backend_normalized_iris_public_key,
                backend_normalized_iris_encrypted_private_key,
                backend_face_public_key,
                backend_face_encrypted_private_key,
                backend_tier2_public_key: user_data.backend_tier2_public_key,
                backend_tier2_encrypted_private_key: user_data.backend_tier2_encrypted_private_key,
                self_custody_user_public_key,
                pcp_version: user_data.pcp_version,
            })
        } else {
            Err(())
        }
    }
```

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

**File:** src/plans/qr_scan/user.rs (L142-157)
```rust
    #[cfg(feature = "internal-data-acquisition")]
    #[must_use]
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
