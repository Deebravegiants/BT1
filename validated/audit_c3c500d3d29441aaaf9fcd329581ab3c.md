Based on my investigation, the most credible analog to the "unhandled return value" bug class in orb-core involves the silent discarding of a `Result::Err` from `TryInto<personal_custody_package::Credentials>`, which allows the signup/enrollment flow to proceed as if the personal custody package (containing the user's encrypted iris/biometric credentials) had been successfully built and uploaded, even when it was not.### Title
Silently ignored `Err` from personal-custody-package credential conversion allows signup to be marked successful without uploading the user's biometric custody package - (File: `src/plans/mod.rs`)

### Summary
`do_signup` converts resolved QR-code/user data into `personal_custody_package::Credentials` via `qr_codes.try_into()` and only acts on the `Ok` branch. The `Err(())` case — returned whenever any of the required backend-issued public/private key fields are missing — is silently swallowed by an `if let Ok(...) = ... { ... }` construct with no `else`. Execution then falls straight through to the enrollment/success-determination logic, which does not depend on whether the custody package was ever built or uploaded. This mirrors the reported ERC20 bug class: a fallible operation's failure signal ("false"/`Err`) is discarded, and the caller proceeds as though the operation succeeded.

### Finding Description
In `src/plans/mod.rs`, `do_signup` performs:

```
if let Ok(mut credentials) = qr_codes.try_into() {
    // ... build_pcp, upload_pcp_tier_0, tier1/tier2 uploads ...
}
``` [1](#0-0) 

The `TryInto<personal_custody_package::Credentials>` implementation for `ResolvedQrCodes` returns `Err(())` whenever any of `backend_iris_public_key`, `backend_iris_encrypted_private_key`, `backend_normalized_iris_public_key`, `backend_normalized_iris_encrypted_private_key`, `backend_face_public_key`, `backend_face_encrypted_private_key`, or `self_custody_user_public_key` is `None`: [2](#0-1) 

Because the `if let Ok(...)` has no corresponding `else` branch, the `Err(())` value is discarded without any logging, metric increment, or abort of the signup flow. Control simply continues to the subsequent code that computes enrollment success:

```
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups {
    debug_report.enrollment_status(match signup_reason {
        SignupReason::Normal => enroll_user::Status::Success,
        _ => enroll_user::Status::Error,
    });
    signup_reason == SignupReason::Normal
} else {
    Box::pin(self.enroll_user(orb, debug_report, &capture, pipeline.as_ref(), signup_reason)).await.is_success()
};
...
result.success = debug_report.enrollment_status.as_ref().map_or(false, enroll_user::Status::is_success);
``` [3](#0-2) 

This block is independent of whether the personal custody package (containing the encrypted iris/face codes and self-custody keys — the durable biometric identity record) was ever built or uploaded. If the conversion fails, the enrollment request to the backend (`enroll_user`) still runs and can report `Success`, and `result.success` can be `true`, even though the client-side custody package containing the user's iris code shares/commitments was never produced or persisted anywhere.

### Impact Explanation
A successful signup can be recorded (debug report marked `signup_successful`, backend enrollment marked `Success`) while the corresponding personal custody package — the artifact that ties the biometric templates to the specific signup/self-custody keys — is silently never built nor uploaded. This creates a state where the orb's local bookkeeping and the backend's enrollment status diverge from the actual presence of custody-package data, i.e., a misattributed/incomplete signup: the user is treated as enrolled without the client having produced the biometric-backed proof material that the flow is designed to always generate. Because the failure is swallowed with no `tracing::error!`, no `dd_incr!` metric, and no distinct `SignupReason`/`SignupStatus`, this failure mode is also invisible to observability/fraud-monitoring pipelines, unlike the properly instrumented failure paths elsewhere in the same function (e.g., `upload_pcp_tier_0`, `build_pcp`).

### Likelihood Explanation
This path is reachable during any normal, unprivileged user signup: whenever backend-provided `UserData` (from `user_status` lookup keyed off the scanned user QR code) is missing any one of the seven required key/ciphertext fields — which can occur due to backend inconsistency, partial provisioning, or race conditions in user-data population — the `Err(())` branch is taken. No special privileges, malicious node, or hardware access is required; it depends entirely on the shape of backend-returned user data at signup time, which is not something the orb enforces or validates before falling through to enrollment.

### Recommendation
Do not discard the `Err(())` case. Explicitly handle the conversion failure by:
1. Logging an error and incrementing a Datadog counter distinguishing this failure mode (similar to other failure paths in `do_signup`).
2. Aborting the signup (returning `Ok(result)` with `result.success = false`) or marking a dedicated `SignupReason`/`SignupStatus` (e.g., an "incomplete user data" failure) instead of letting `success` be computed independently of custody-package availability.
3. Ideally, replacing the `()` error type with a descriptive error enum indicating exactly which field(s) were missing, to aid debugging and prevent future silent-discard patterns.

### Proof of Concept
1. Arrange (or simulate via backend/test double) `user_status` data for a given user QR code where one of the seven required fields (e.g., `backend_face_encrypted_private_key`) is `None`.
2. Proceed through a normal signup: `scan_remaining_qr_codes` → `biometric_capture` → `biometric_pipeline` → `detect_fraud`.
3. At `qr_codes.try_into()` (`src/plans/mod.rs:574`), the conversion returns `Err(())`; the `if let Ok(...)` block (lines 574-637), including `build_pcp`/`upload_pcp_tier_0`, is skipped entirely — no error is logged.
4. Execution continues to the `let success = ...` block (lines 639-656), which calls `enroll_user` (or short-circuits for user-centric signups) and can yield `Status::Success`.
5. `result.success` becomes `true` and `debug_report.signup_successful()` may be invoked, even though no personal custody package was ever built or uploaded for this signup — with no error signal anywhere in logs/metrics identifying the discarded conversion failure.

### Citations

**File:** src/plans/mod.rs (L572-598)
```rust
        let user_id = qr_codes.user_qr_code.user_id.clone();
        let user_centric_signup = qr_codes.user_data.user_centric_signup;
        if let Ok(mut credentials) = qr_codes.try_into() {
            let personal_custody_package::Credentials { pcp_version, .. } = &mut credentials;
            if !pcp_v3 {
                *pcp_version = 2;
            }
            let pcp_version = *pcp_version;
            let packages = match Box::pin(self.build_pcp(
                orb,
                credentials,
                &capture,
                pipeline.as_ref(),
                debug_report,
                signup_reason,
            ))
            .await
            {
                Ok(Some(p)) => p,
                Ok(None) => {
                    return Ok(result);
                }
                Err(e) => {
                    tracing::error!("{e}");
                    return Ok(result);
                }
            };
```

**File:** src/plans/mod.rs (L639-662)
```rust
        let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
        {
            debug_report.enrollment_status(match signup_reason {
                SignupReason::Normal => enroll_user::Status::Success,
                _ => enroll_user::Status::Error,
            });
            signup_reason == SignupReason::Normal
        } else {
            Box::pin(self.enroll_user(
                orb,
                debug_report,
                &capture,
                pipeline.as_ref(),
                signup_reason,
            ))
            .await
            .is_success()
        };

        Self::report_signup_reason(success, signup_reason, debug_report);

        result.success =
            debug_report.enrollment_status.as_ref().map_or(false, enroll_user::Status::is_success);
        Ok(result)
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
