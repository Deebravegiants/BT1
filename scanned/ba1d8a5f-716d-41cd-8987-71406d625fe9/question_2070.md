# Q2070: Signed payload construction in upload_all_signup_images is ambiguous (agents/image_uploader.rs)

## Question
Can an unprivileged attacker exploit non-canonical serialization in `upload_all_signup_images` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) (map ordering, optional fields, unescaped separators) so two different logical payloads produce the same signed bytes, letting one Orb signature authenticate a different claim?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `upload_all_signup_images` (function)
- Entrypoint: Attacker-controlled string fields that end up inside the signed payload
- Attacker controls: content of identity/metadata fields that are concatenated into the signed bytes
- Exploit idea: Look for length-prefixing and canonical encoding in `upload_all_signup_images`; without it, field-boundary shifting creates collisions.
- Invariant to test: The signed byte string is an injective, canonical encoding of the logical payload.
- Expected Immunefi impact: Orb-signed attestation authenticating a claim the Orb never made
- Fast validation: Differential test constructing two distinct payloads through `upload_all_signup_images` and asserting distinct signed bytes.
