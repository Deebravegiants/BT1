# Q1952: Custody package encrypted to an attacker-supplied key in to_uuid (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker supply the self-custody public key/identity material through their scanned payload so `to_uuid` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) encrypts or addresses the biometric custody package to a key of the attacker's choosing rather than one bound to the verified user?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `to_uuid` (function)
- Entrypoint: Identity/key material carried in the scanned QR payload
- Attacker controls: the public key bytes and identity fields in the payload
- Exploit idea: Trace the key used by `to_uuid` back to its origin and check for authenticity binding before use.
- Invariant to test: Custody material is encrypted only to a key whose binding to the enrolling user is verified.
- Expected Immunefi impact: Another person's biometric package recoverable by the attacker
- Fast validation: Integration test substituting an attacker key and asserting the package build is refused.
