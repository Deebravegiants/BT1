### Title
User QR-code `user_id` parsing accepts a truncated/reduced-entropy UUID as equivalent to a full 128-bit UUIDv4, mixing two ID "precisions" in the signup trust anchor - (File: src/plans/qr_scan/user.rs)

### Summary
`GenericLogic.sol` incorrectly assumed all price feeds shared a common decimal precision and summed heterogeneous-precision values as if they were homogeneous, corrupting the health-factor calculation. The `QR_CODE_V2` regex in `src/plans/qr_scan/user.rs` makes an analogous "same precision" assumption about the `user_id` field: it is documented as a "128-bit UUIDv4" but the regex accepts a shortened variant (only the first two hyphen groups, 16 hex chars / 64 bits) as an equally valid `user_id`, and this value flows unchanged into the signup/session trust boundary.

### Finding Description
`Data::from_v2` is built from the `QR_CODE_V2` regex: [1](#0-0) 

The `user_id` capture group is defined so the last two hyphenated groups (`-xxxx-xxxxxxxxxxxx`, 64 of the 128 bits) are optional, i.e. `8-4-4` alone matches just as well as the full `8-4-4-4-12` UUID. This is confirmed by the codebase's own test: [2](#0-1) 

`Data` documents `user_id` as "User ID in format of 128-bit UUIDv4" and treats both the full and shortened forms as the same type with no distinction or normalization: [3](#0-2) 

This `user_id` string is used, unmodified, as the trust anchor for the entire signup flow: it's compared to the operator QR to reject collisions, sent directly to the backend to fetch/validate a session, and later used to tag uploaded biometric packages (PCP tiers) and identity binding. [4](#0-3) [5](#0-4) [6](#0-5) 

Just as `GenericLogic.sol` summed collateral/debt values from feeds of different decimal precision as if they had one consistent precision, `try_parse` accepts `user_id` values of two different entropy "precisions" (128-bit vs 64-bit) as if they were the same canonical identifier space, and neither this function nor its downstream consumers (`verify_user_qr_code`, `backend::user_status::request`, PCP upload tagging) normalize, reject, or flag the reduced-precision case.

### Impact Explanation
A reduced-entropy `user_id` weakens the uniqueness guarantee that the rest of the signup pipeline implicitly relies on (operator-vs-user QR collision check, backend session lookup, PCP tier upload keyed by `user_id`). Because the shortened form is silently accepted as a fully valid identifier rather than being rejected or normalized to the canonical 128-bit space, it raises the risk of a signup being bound to, or its biometric package uploaded/keyed under, an unintended/colliding session identifier — a cross-signup state bleed / misattributed-signup class of impact, mirroring how mixed-decimal price feeds silently produced a wrong aggregate health factor instead of failing loudly.

### Likelihood Explanation
This path is reachable by any unprivileged user/operator presenting a QR code during a normal signup — no privileged access or malicious node/hardware access is required, since `try_parse` is invoked on every scanned user QR code in the standard signup flow. The likelihood of an accidental or deliberately truncated `user_id` colliding with another legitimate 64-bit-truncated ID is non-negligible relative to the intended 128-bit design and is directly enabled by the regex accepting an entropy class the type's own documentation says shouldn't exist.

### Recommendation
Reject `user_id` values that do not match the full canonical 128-bit UUIDv4 format at parse time (remove the optional trailing groups from `QR_CODE_V2`), or explicitly normalize/flag shortened identifiers so downstream backend/session/PCP-tagging logic never treats a reduced-entropy ID as equivalent to a full UUID.

### Proof of Concept
The existing unit test itself demonstrates the acceptance of the non-canonical, reduced-precision identifier as a fully valid `user_id`:
```rust
#[test]
fn test_v2_shortened() {
    let text = "userid:3bcf883d-ce22-4a03:1";
    let data = Data::from_v2(&QR_CODE_V2.captures(text).unwrap());
    assert_eq!(data.user_id, "3bcf883d-ce22-4a03"); // only 16 hex chars, not a 128-bit UUID
    assert!(data.signup_extension_config.is_none());
}
``` [2](#0-1)

### Citations

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

**File:** src/plans/qr_scan/user.rs (L230-236)
```rust
    #[test]
    fn test_v2_shortened() {
        let text = "userid:3bcf883d-ce22-4a03:1";
        let data = Data::from_v2(&QR_CODE_V2.captures(text).unwrap());
        assert_eq!(data.user_id, "3bcf883d-ce22-4a03");
        assert!(data.signup_extension_config.is_none());
    }
```

**File:** src/plans/mod.rs (L572-572)
```rust
        let user_id = qr_codes.user_qr_code.user_id.clone();
```

**File:** src/plans/mod.rs (L1036-1044)
```rust
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

**File:** src/backend/user_status.rs (L119-133)
```rust
    let request = if use_only_operator_location {
        super::client()?
            .get(format!("{}/api/v2/session/{}/status", *SIGNUP_BACKEND_URL, qr_code.user_id,))
            .query(&[
                ("lat", operator_data.location_data.session_coordinates.latitude),
                ("lon", operator_data.location_data.session_coordinates.longitude),
            ])
    } else if use_full_operator_qr {
        super::client()?
            .get(format!("{}/api/v2/session/{}/status", *SIGNUP_BACKEND_URL, qr_code.user_id))
            .query(&[("operator_id", &operator_data.qr_code.user_id)])
    } else {
        super::client()?
            .get(format!("{}/api/v1/user/{}/status", *SIGNUP_BACKEND_URL, qr_code.user_id))
    }
```
