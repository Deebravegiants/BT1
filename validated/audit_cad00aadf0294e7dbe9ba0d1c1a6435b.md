### Title
Unvalidated `skip-user-qr-validation` build-time flag disables identity-binding verification of signup QR data - ([File: src/backend/user_status.rs])

### Summary
The Nouns finding centers on security-critical parameters (`delayedGovernanceMaxDuration`, voting/threshold parameters) that are set once outside the normal governance/proposal flow, are never bounds-checked, and whose misconfiguration (e.g., value `0`) silently disables a downstream security control (`checkGovernanceActive()`), enabling theft. The structural analog in `orb-core` is the `skip-user-qr-validation` Cargo feature, which is combined at build time (outside any runtime signup flow, unchecked by any validation logic) and, when active, disables `user_data.verify(user_data_hash)` — the check that cryptographically binds the user QR-code payload to the backend-issued `authenticated_app_data`.

### Finding Description
`orb-core`'s user identity validation flow in `backend::user_status::request()` performs a critical identity-binding step: it verifies that the `user_data` returned by the backend actually corresponds to the QR code that was physically scanned, by hashing/verifying `qr_code.user_data_hash` against the backend-authenticated data: [1](#0-0) 

This check is entirely gated by `#[cfg(not(feature = "skip-user-qr-validation"))]`. If the `skip-user-qr-validation` feature is enabled, the verification block is compiled out entirely, and the code proceeds directly to trust `backend_keys`/`authenticated_app_data` without confirming they belong to the scanned QR code.

This feature flag is defined in the crate manifest and, critically, is not gated behind any runtime configuration, proposal-like review process, or validation logic in the code itself — much like `ForkDAODeployer`'s constructor parameters, it is set once at build time and has no in-code bound/consistency check: [2](#0-1) 

Just as the Nouns report shows that `delayedGovernanceMaxDuration = 0` silently disables `checkGovernanceActive()` with catastrophic consequences, enabling `skip-user-qr-validation` silently disables the identity-binding check (`user_data.verify(user_data_hash)`) that guarantees the encryption keys and identity commitment returned by the backend are attributable to the exact QR code the person in front of the Orb presented.

### Impact Explanation
If a build variant with `skip-user-qr-validation` is deployed or accidentally enabled (this feature is only supposed to be used for internal PCP export tooling — it's bundled together with `internal-pcp-export` and `internal-pcp-no-encryption`, none of which are runtime-validated or logged as a security-relevant deviation), the Orb would accept `backend_iris_public_key`, `backend_face_public_key`, `self_custody_user_public_key`, and `identity_commitment` without confirming they are cryptographically tied to the physically-presented user QR code. This breaks the core identity-binding guarantee of the signup flow: an attacker able to influence which `user_data`/keys get associated with a QR-code interaction (e.g., via a compromised/misconfigured backend response, or a MITM on data en route, in a build where this flag is set) could cause cross-signup state bleed — biometric enrollment data or self-custody keys attributed to the wrong identity/QR-code presenter. This is analogous to the reported "misattributed treasury ownership" impact: instead of misattributed governance/funds, it is misattributed identity binding at signup.

### Likelihood Explanation
Likelihood is low, matching the "Medium" severity rating and rationale used in the original report: the feature must be intentionally compiled into a production-facing build, which should not normally happen since it's meant strictly for internal PCP export tooling. However, because there is no runtime assertion, telemetry, or check in the code (analogous to no on-chain bound-checking of the fork parameters) that a non-standard, security-weakening build variant is running, a misconfiguration during build/release (operational mistake) would go undetected, exactly the concern raised in the Nouns report about hard-to-review, one-time-set parameters.

### Recommendation
Add an explicit runtime assertion or startup check that panics/refuses to run signups if `skip-user-qr-validation` is compiled in outside of an explicitly-flagged internal/dev environment (mirroring the recommendation to bound-check fork parameters at construction time rather than trust them implicitly). Additionally, consider making this check impossible to silently disable in release/production builds — e.g., via a `compile_error!` guard combined with the `stage`/production feature flags, or by moving the verification to a runtime code path that cannot be feature-gated out.

### Proof of Concept
1. Build `orb-core` with `--features skip-user-qr-validation` (which also pulls in `internal-pcp-export` and `internal-pcp-no-encryption`).
2. In `backend::user_status::request()`, the block performing `user_data.verify(user_data_hash)` is compiled out: [3](#0-2) 
3. Present a QR code to the Orb; regardless of whether the backend's `authenticated_app_data` is actually bound to that scanned QR-code payload, `request()` returns `Ok(Some(UserData { .. }))` using the backend-provided keys/identity commitment without verification, allowing the signup pipeline (`enroll_user`, PCP creation via `TryInto<personal_custody_package::Credentials>`) to proceed with unverified identity-binding data: [4](#0-3) 

Note: I was unable to fully trace how or whether this feature is ever accidentally included in Orb fleet release pipelines (that CI/build configuration lives outside the indexed `orb-core` sources), so the actual operational likelihood of this flag being set in a fielded Orb is uncertain and would need confirmation from the release/build tooling.

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

**File:** Cargo.toml (L119-130)
```text
allow-plan-mods = []                                                        # Allows modifications to the plans.
cuda-test = ["orb-rgb-net/cuda-test", "orb-ir-net/cuda-test"]
debug-eye-tracker = []                                                      # Enables println outputs in eye_tracker.rs
integration_testing = []                                                    # Enable hacks for passing integration tests on CI
internal-data-acquisition = []                                              # Advanced and verbose imaging for R&D purposes.
livestream = ["dep:egui", "dep:egui-wgpu", "dep:egui-phosphor"]             # Enable livestream agent to debug cameras
log-iris-data = []                                                          # Allows logging of iris codes and mask codes
no-image-encryption = []
internal-pcp-export = []
internal-pcp-no-encryption = []
skip-user-qr-validation = ["internal-pcp-export", "internal-pcp-no-encryption"]
stage = ["dep:local-ip-address", "livestream", "agentwire/sandbox-network"] # Use staging backend
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
