### Title
Self-Signup Guard Relies on Trivial QR-Code Identifier Equality, Allowing an Operator to Bypass the Same-Identity Restriction with a Second Identity - (File: src/plans/mod.rs)

### Summary
The Orb prevents an operator from enrolling themselves as their own "user" during a signup session by comparing the scanned user QR-code's `user_id` against the operator QR-code's `user_id` and rejecting the scan if they match [1](#0-0) . Just like the CSX `ReferralRegistry` self-referral check that compares `refOwner == buyer` by address and can be bypassed by registering the referral code from a second address, this Orb check only compares string identifiers extracted from QR codes and can be trivially bypassed by presenting a *second* QR-code identity for the very same human operator/user.

### Finding Description
The anti-self-signup guard lives in `handle_user_qr_code`:

```
// Filter out the operator QR code
if user_qr_code.user_id == operator_data.qr_code.user_id {
    ...
    return Ok(None);
}
``` [1](#0-0) 

This is the exact same class of check as the CSX bug: it establishes "not the same actor" by comparing a single opaque identifier (`user_id` string) rather than any robust, biometrically-bound identity. Nothing in `orb-core` ties the `user_id` field of a QR code to a specific human being at scan time — the QR code is simply parsed user input (`qr_scan::user::Data`) [2](#0-1) , and the same physical person can trivially obtain a second, distinct `user_id`-bearing QR code (e.g., a second app installation/account) exactly as a blockchain user can trivially obtain a second address.

The operator's identity feeds directly into the backend signup request as the `distributorId` field, which attributes/credits the signup to that operator:

```
let mut form = Form::new()
    ...
    .text("distributorId", operator_qr_code.user_id.clone())
    .text("userId", user_qr_code.user_id.clone())
``` [3](#0-2) 

Because the only control preventing an operator from being both "distributor" and "signed-up user" is the trivial string-equality check at line 1036, an operator can defeat it the same way the referral-code owner defeats the buyer-owner check in the reported bug class: simply present a *different* `user_id` (a second self-controlled identity/QR code) as the "user" while scanning their own operator QR code as the distributor. The orb-side logic has no mechanism to detect that the operator identity and the "user" identity belong to the same real-world person beyond this single identifier comparison.

### Impact Explanation
This allows a misattributed signup: an operator can enroll themselves at their own Orb while being credited as the distributor for that signup, bypassing the intended restriction that an operator cannot be their own referred/distributed user. This is a direct code-level analog of the reported medium-risk self-referral discount abuse — the safeguard is based purely on account/identifier equality and is defeated by using a second identifier for the same actor, resulting in unintended crediting/attribution of a signup to an operator who is also the enrolled subject.

### Likelihood Explanation
Likelihood is high for any operator wishing to abuse this: obtaining a second `user_id`-bearing QR code requires no privileged access, no hardware tampering, and no interaction with a malicious peer/node — it only requires generating a second app/account identity, which is fully within reach of a normal, unprivileged operator/user. The check is purely client-side string comparison at scan time in `handle_user_qr_code`, and is bypassed with zero cryptographic effort.

### Recommendation
Do not rely solely on QR-code `user_id` string equality to prevent self-signup/self-referral attribution. Enforce the restriction on the backend using a robust, biometrically-bound identity check (e.g., verifying the enrolled iris/identity does not match the operator's own enrolled identity, or requiring out-of-band KYC/whitelisting of distributor accounts as suggested in the referenced report), rather than trusting client-presented identifiers that can be multiplied at will.

### Proof of Concept
1. An operator scans their own operator QR-code (`user_id = A`) to start a signup session, per `scan_operator_qr_code`/`verify_operator_qr_code` [4](#0-3) .
2. Instead of scanning that same QR code as the "user," the operator scans a second, self-controlled QR-code identity (`user_id = B`, obtained by registering a second app account) as the user.
3. `handle_user_qr_code` compares `user_qr_code.user_id` (`B`) against `operator_data.qr_code.user_id` (`A`); since `B != A`, the equality check at line 1036 passes and the scan is accepted [5](#0-4) .
4. The signup proceeds normally through `do_signup`/`enroll_user`, and the backend request sets `distributorId = A` and `userId = B` [3](#0-2) , crediting operator `A` as the distributor for a signup that is, in reality, `A` enrolling themself under a second identity.

### Citations

**File:** src/plans/mod.rs (L1029-1044)
```rust
        let (user_qr_code, user_qr_code_string) = match scan_result {
            Ok((user_qr_code, user_qr_code_string)) => {
                dd_incr!("main.count.signup.during.general.user_qr_code_detected");
                tracing::info!("User QR-code detected: {user_qr_code:?}");
                orb.ui.qr_scan_completed(QrScanSchema::User);

                // Filter out the operator QR code
                if user_qr_code.user_id == operator_data.qr_code.user_id {
                    orb.ui.qr_scan_unexpected(QrScanSchema::User, QrScanUnexpectedReason::Invalid);
                    tracing::info!("User QR-code is the same as the operator QR-code, retrying");
                    // Give time to remove the QR code from the front of the camera
                    sleep(Duration::from_millis(1500)).await;
                    #[cfg(not(feature = "integration_testing"))]
                    return Ok(None);
                }
                (user_qr_code, user_qr_code_string)
```

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

**File:** src/plans/qr_scan/user.rs (L71-82)
```rust
/// User QR-code data.
#[derive(Default, Clone, Debug)]
pub struct Data {
    /// User ID in format of 128-bit UUIDv4.
    pub user_id: String,
    /// It's a data acquisition QR code.
    pub signup_extension: bool,
    /// Data acquisition configuration.
    pub signup_extension_config: Option<SignupExtensionConfig>,
    /// Hash of the user data stored in the backend.
    pub user_data_hash: Option<Vec<u8>>,
}
```

**File:** src/backend/signup_post.rs (L125-129)
```rust
    let mut form = Form::new()
        .text("softwareVersion", &*ORB_OS_VERSION)
        .text("orbId", ORB_ID.as_str())
        .text("distributorId", operator_qr_code.user_id.clone())
        .text("userId", user_qr_code.user_id.clone())
```
