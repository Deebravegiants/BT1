# Q1866: Signed payload construction in make_info_json is ambiguous (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker exploit non-canonical serialization in `make_info_json` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) (map ordering, optional fields, unescaped separators) so two different logical payloads produce the same signed bytes, letting one Orb signature authenticate a different claim?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_info_json` (function)
- Entrypoint: Attacker-controlled string fields that end up inside the signed payload
- Attacker controls: content of identity/metadata fields that are concatenated into the signed bytes
- Exploit idea: Look for length-prefixing and canonical encoding in `make_info_json`; without it, field-boundary shifting creates collisions.
- Invariant to test: The signed byte string is an injective, canonical encoding of the logical payload.
- Expected Immunefi impact: Orb-signed attestation authenticating a claim the Orb never made
- Fast validation: Differential test constructing two distinct payloads through `make_info_json` and asserting distinct signed bytes.
