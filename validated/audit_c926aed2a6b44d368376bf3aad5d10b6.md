### Title
User QR-code allows a truncated/shortened UUID to be accepted as a valid `user_id`, enabling collision-based misattribution risk - (File: src/plans/qr_scan/user.rs)

### Summary
Analogous to the Bio NFT bug — where the line-break logic silently truncates/misparses long input so that different-length strings render identically — `orb-core`'s user QR-code regex `QR_CODE_V2` accepts a shortened UUID prefix (the first 18 characters, i.e. the `xxxxxxxx-xxxx-xxxx` segments) as a complete, valid `user_id`, because the remaining `-xxxx-xxxxxxxxxxxx` segment is optional in the regex.

### Finding Description
`QR_CODE_V2` is defined with the last UUID group wrapped in `(?:...)?`, making it optional: [1](#0-0) 

This means a QR code such as `userid:3bcf883d-ce22-4a03:1` (an 18-character truncated identifier) is parsed successfully and treated exactly like a full 36-character UUID would be, which is explicitly confirmed by the existing unit test: [2](#0-1) 

This is the same class of defect as the Bio NFT SVG bug: the parser does not enforce that the full expected length/structure is present, so a shortened input is silently accepted as if it were the canonical, full-length value — different inputs (a full UUID vs. its 18-character prefix) end up being treated as equivalent/interchangeable identifiers by the client-side parser, analogous to the two differently-sized bio strings rendering as identical SVGs.

The parsed (possibly truncated) `user_id` string is subsequently used as the identity token for the signup flow — it is sent to the backend for validation via `backend::user_status::request`, compared against the operator QR-code's `user_id` for equality (`user_qr_code.user_id == operator_data.qr_code.user_id`) as an anti-collision check, and threaded through the signup-post flow: [3](#0-2) 

### Impact Explanation
If the truncated 18-character prefix is accepted by the orb as a legitimate `user_id` and forwarded to the backend/signup pipeline, any two full UUIDs sharing the same 18-character prefix would be indistinguishable to this client-side check, or an attacker/operator could intentionally present a truncated QR-code value to bypass exact-match logic (e.g., the same-as-operator-QR-code de-duplication check at `user_qr_code.user_id == operator_data.qr_code.user_id`). This creates a plausible path toward misattributed or colliding signup identity, since the orb's own parsing layer does not enforce that the identifier is complete before treating it as authoritative. The severity ultimately depends on whether the backend performs its own strict validation of `user_id` format/length, which is outside `orb-core`.

### Likelihood Explanation
Likelihood is low-to-moderate: it requires an attacker or malfunctioning/malicious QR generator to produce a shortened `userid:` QR code, which is plausible since this is a standard, unprivileged user-facing scan path (the same one exercised by `qr_scan::user::Data::try_parse`) and requires no special access. Whether it is practically exploitable further depends on backend-side strictness, which cannot be confirmed from this repository alone.

### Recommendation
Remove the optional group from `QR_CODE_V2` (or otherwise require the full 36-character UUID structure) so that only complete UUIDs are accepted as `user_id`. If shortened identifiers are intentionally supported for some legacy/testing reason, restrict that acceptance to explicit test/CLI code paths (as is already partially the case for `QR_CODE_SIGNUP_EXTENSION`) and never accept it in the production signup path, and additionally validate the parsed `user_id` length/format before using it in equality checks or backend requests.

### Proof of Concept
Using the existing test in the codebase as a proof of concept: [2](#0-1) 

A QR code payload of `userid:3bcf883d-ce22-4a03:1` (18-character truncated UUID) is accepted by `Data::try_parse`/`Data::from_v2` and produces `user_id == "3bcf883d-ce22-4a03"`, which is then usable anywhere a full UUID `user_id` would be used in `src/plans/mod.rs`, exactly mirroring how the Bio NFT contract silently accepted and mis-rendered an over-length/malformed string as if it were valid.

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
