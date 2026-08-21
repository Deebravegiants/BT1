# Q0725: Signed payload construction in read_orb_id is ambiguous (identification.rs)

## Question
Can an unprivileged attacker exploit non-canonical serialization in `read_orb_id` in [src/identification.rs](src/identification.rs) (map ordering, optional fields, unescaped separators) so two different logical payloads produce the same signed bytes, letting one Orb signature authenticate a different claim?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `read_orb_id` (function)
- Entrypoint: Attacker-controlled string fields that end up inside the signed payload
- Attacker controls: content of identity/metadata fields that are concatenated into the signed bytes
- Exploit idea: Look for length-prefixing and canonical encoding in `read_orb_id`; without it, field-boundary shifting creates collisions.
- Invariant to test: The signed byte string is an injective, canonical encoding of the logical payload.
- Expected Immunefi impact: Orb-signed attestation authenticating a claim the Orb never made
- Fast validation: Differential test constructing two distinct payloads through `read_orb_id` and asserting distinct signed bytes.
