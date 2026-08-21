# Q3065: Signed payload construction in sign is ambiguous (secure_element.rs)

## Question
Can an unprivileged attacker exploit non-canonical serialization in `sign` in [src/secure_element.rs](src/secure_element.rs) (map ordering, optional fields, unescaped separators) so two different logical payloads produce the same signed bytes, letting one Orb signature authenticate a different claim?

## Target
- File/function: [src/secure_element.rs](src/secure_element.rs) -> `sign` (function)
- Entrypoint: Attacker-controlled string fields that end up inside the signed payload
- Attacker controls: content of identity/metadata fields that are concatenated into the signed bytes
- Exploit idea: Look for length-prefixing and canonical encoding in `sign`; without it, field-boundary shifting creates collisions.
- Invariant to test: The signed byte string is an injective, canonical encoding of the logical payload.
- Expected Immunefi impact: Orb-signed attestation authenticating a claim the Orb never made
- Fast validation: Differential test constructing two distinct payloads through `sign` and asserting distinct signed bytes.
