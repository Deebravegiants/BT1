I've completed the investigation. Here are the results:

### Title
Truncated/shortened user QR-code identifier silently accepted as valid `user_id` during signup - (File: `src/plans/qr_scan/user.rs`)

### Summary
The `QR_CODE_V2` regex used to parse user-scanned QR codes accepts a shortened, non-standard UUID (only the first two hyphen-delimited groups, `8-4-4`) as a fully valid `user_id`, because the trailing `4-12` UUID segments are wrapped in an optional non-capturing group. This mirrors the ENS `hexToAddress` bug class: an identifier of the wrong/truncated length is silently accepted instead of being rejected, and the truncated value is carried forward as the authoritative identity for the rest of the signup flow.

### Finding Description
`QR_CODE_V2` is defined with the last two UUID segments made optional via `(?: - [a-z0-9]{4} - [a-z0-9]{12} )?`: [1](#0-0) 

This means a code like `userid:3bcf883d-ce22-4a03:1` (a 16-character truncated identifier instead of the expected 36-character UUID) is captured successfully and turned into `Data.user_id` verbatim, as demonstrated by the existing test: [2](#0-1) 

`Data::from_v2` copies the captured string as-is into `user_id` with no length/format re-validation: [3](#0-2) 

This `user_id` string is then used, unvalidated, as the actual session/user identity throughout the signup pipeline: it's sent to the backend for user QR-code validation via `/api/v1/user/{user_id}/status` or `/api/v2/session/{user_id}/status`, and later as the `userId`/`distributorId` field in the signup submission request: [4](#0-3) [5](#0-4) 

It is also hashed into the biometric enrollment signature together with the iris/face codes: [6](#0-5) 

Unlike the modern `decode_qr` path (which decodes a structured/authenticated binary payload into a `Uuid`), the legacy/plaintext `userid:...` QR path performs no canonical UUID validation — it only checks the input against a permissive regex that allows a truncated identifier through. [7](#0-6) 

### Impact Explanation
Orb-core is the client-side trust boundary for what counts as a "valid user QR code" before initiating the signup and biometric-enrollment workflow. By accepting a shortened/malformed identifier as a legitimate `user_id`, orb-core forwards an ambiguous, non-canonical identity string to the backend as the authoritative user/session reference for the entire signup (status check, biometric key retrieval, and final signup submission with `distributorId`/`userId`). If the backend performs any prefix-tolerant or loosely-typed lookup on this string (mirroring the exact class of bug in the ENS report — accepting a wrong-length value and deriving something from a partial match), a truncated ID supplied by an unprivileged user (anyone who can present/generate a QR code to the orb) could result in a signup being processed under, or attributed to, an unintended session/user identity — a cross-signup identity/state-bleed risk analogous to the reported ENS ownership misattribution. Even absent backend-side compounding, this is a case of orb-core failing to enforce the documented identifier format ("User ID in format of 128-bit UUIDv4") at the trust boundary where user-supplied QR content is first parsed. [8](#0-7) 

### Likelihood Explanation
Low-to-moderate: it requires an unprivileged party to present a QR code with a deliberately truncated `userid:` payload (three UUID groups instead of five) to the orb during the user-scan step of a signup, which is straightforward to construct since the format is public and unauthenticated (plain regex-matched string, no signature). The unusual, non-standard 16-character identifier would likely fail most backend session lookups outright, but the client itself provides no defense-in-depth check, so any looseness on the backend side is not mitigated by orb-core.

### Recommendation
Require the `user_id` capture group in `QR_CODE_V2` (and `QR_CODE_SIGNUP_EXTENSION` where applicable) to match a complete, canonical UUID format only — remove the `?` that makes the trailing `4-12` segments optional, or explicitly validate the captured string with a proper UUID parser (e.g. `uuid::Uuid::parse_str`) and reject the QR code (`try_parse` returns `None`) if it doesn't parse as a well-formed UUID, rather than silently accepting the truncated value.

### Proof of Concept
```rust
// src/plans/qr_scan/user.rs, existing test demonstrates the truncation is accepted:
let text = "userid:3bcf883d-ce22-4a03:1";
let data = Data::from_v2(&QR_CODE_V2.captures(text).unwrap());
assert_eq!(data.user_id, "3bcf883d-ce22-4a03"); // 16-char truncated "UUID" accepted as-is
```
This truncated `user_id` then flows unchecked into `backend::user_status::do_request` (as the path segment for `/api/v1/user/{user_id}/status`) and into `backend::signup_post::request` (as the `userId` form field), i.e. it becomes the canonical identity reference for the rest of the signup. [2](#0-1) [9](#0-8)

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

**File:** src/plans/qr_scan/user.rs (L72-82)
```rust
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

**File:** src/plans/qr_scan/user.rs (L106-124)
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
}
```

**File:** src/plans/qr_scan/user.rs (L126-140)
```rust
impl Data {
    #[must_use]
    fn from_v2(captures: &Captures) -> Self {
        let user_id = captures
            .name("user_id")
            .expect("user_id capture group must be present")
            .as_str()
            .to_string();
        Self {
            user_id,
            signup_extension: false,
            signup_extension_config: None,
            user_data_hash: None,
        }
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

**File:** src/backend/signup_post.rs (L125-133)
```rust
    let mut form = Form::new()
        .text("softwareVersion", &*ORB_OS_VERSION)
        .text("orbId", ORB_ID.as_str())
        .text("distributorId", operator_qr_code.user_id.clone())
        .text("userId", user_qr_code.user_id.clone())
        .text("region", s3_region.to_owned())
        .text("signature", signature.map_or(String::default(), Clone::clone))
        .text("codes", codes)
        .text("reason", signup_reason.to_screaming_snake_case().to_string());
```

**File:** src/plans/enroll_user.rs (L290-303)
```rust
fn make_signature(user_qr_code: &qr_scan::user::Data, pipeline: &Pipeline) -> Result<String> {
    let mut ctx = Context::new(&SHA256);
    ctx.update(ORB_ID.as_str().as_bytes());
    ctx.update(user_qr_code.user_id.as_bytes());
    ctx.update(pipeline.v2.ir_net_version.as_bytes());
    ctx.update(pipeline.v2.iris_version.as_bytes());
    ctx.update(pipeline.v2.eye_left.iris_code.as_bytes());
    ctx.update(pipeline.v2.eye_left.mask_code.as_bytes());
    ctx.update(pipeline.v2.eye_left.iris_code_version.as_bytes());
    ctx.update(pipeline.v2.eye_right.iris_code.as_bytes());
    ctx.update(pipeline.v2.eye_right.mask_code.as_bytes());
    ctx.update(pipeline.v2.eye_right.iris_code_version.as_bytes());
    let signed = secure_element::sign(ctx.finish())?;
    Ok(BASE64.encode(&signed))
```
