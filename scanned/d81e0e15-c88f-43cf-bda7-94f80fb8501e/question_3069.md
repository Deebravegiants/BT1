# Q3069: Custody package encrypted to an attacker-supplied key in read_orb_id (identification.rs)

## Question
Can an unprivileged attacker supply the self-custody public key/identity material through their scanned payload so `read_orb_id` in [src/identification.rs](src/identification.rs) encrypts or addresses the biometric custody package to a key of the attacker's choosing rather than one bound to the verified user?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `read_orb_id` (function)
- Entrypoint: Identity/key material carried in the scanned QR payload
- Attacker controls: the public key bytes and identity fields in the payload
- Exploit idea: Trace the key used by `read_orb_id` back to its origin and check for authenticity binding before use.
- Invariant to test: Custody material is encrypted only to a key whose binding to the enrolling user is verified.
- Expected Immunefi impact: Another person's biometric package recoverable by the attacker
- Fast validation: Integration test substituting an attacker key and asserting the package build is refused.
