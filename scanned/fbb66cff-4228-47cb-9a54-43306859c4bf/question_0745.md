# Q0745: Signed payload construction in get_sharpest_frame is ambiguous (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit non-canonical serialization in `get_sharpest_frame` in [src/agents/image_notary.rs](src/agents/image_notary.rs) (map ordering, optional fields, unescaped separators) so two different logical payloads produce the same signed bytes, letting one Orb signature authenticate a different claim?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `get_sharpest_frame` (function)
- Entrypoint: Attacker-controlled string fields that end up inside the signed payload
- Attacker controls: content of identity/metadata fields that are concatenated into the signed bytes
- Exploit idea: Look for length-prefixing and canonical encoding in `get_sharpest_frame`; without it, field-boundary shifting creates collisions.
- Invariant to test: The signed byte string is an injective, canonical encoding of the logical payload.
- Expected Immunefi impact: Orb-signed attestation authenticating a claim the Orb never made
- Fast validation: Differential test constructing two distinct payloads through `get_sharpest_frame` and asserting distinct signed bytes.
